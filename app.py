import os
from dotenv import load_dotenv  # 新增：加载保险箱工具
import google.generativeai as genai
from flask import Flask, render_template, request, jsonify
import random
import time
# 加载 .env 文件里的秘密信息
load_dotenv()
# ==========================================
# 0. 绝对路径配置
# ==========================================
BASE_DIR = os.path.abspath(os.path.dirname(__file__))
STATIC_DIR = os.path.join(BASE_DIR, 'YVstatic')
TEMPLATE_DIR = os.path.join(BASE_DIR, 'templates')

# ==========================================
# 1. 环境配置 (代理与 AI 引擎)
# ==========================================
proxy_port = "2712"
os.environ['http_proxy'] = f'http://127.0.0.1:{proxy_port}'
os.environ['https_proxy'] = f'http://127.0.0.1:{proxy_port}'

app = Flask(__name__,
            static_folder=STATIC_DIR,
            static_url_path='/YVstatic',
            template_folder=TEMPLATE_DIR)

# 变成从环境变量拿 Key
api_key = os.getenv("GEMINI_API_KEY")
genai.configure(api_key=api_key, transport='rest')
model = genai.GenerativeModel('gemini-1.5-flash')


# ==========================================
# 2. 路由控制
# ==========================================

@app.route('/')
def index():
    return render_template('index.html')


@app.route('/analyze', methods=['POST'])
def analyze_emotion():
    data = request.json
    user_text = data.get('text', '')
    print(f"\n[1. 信号接收] 收到情绪内容：{user_text}")

    score = 50
    if any(word in user_text for word in ['开', '好', '棒', '喜', '乐']): score = 85
    if any(word in user_text for word in ['难', '哭', '压', '累', '愁']): score = 20

    try:
        print(f"[2. 深度识别] 正在通过 {proxy_port} 端口联络 Google AI...")
        prompt = f"你是一个专业的情绪分析引擎。请分析这段文字的情绪，并仅返回一个0-100的整数（0最悲伤，100最快乐）。内容：{user_text}"

        response = model.generate_content(prompt)
        score_text = ''.join(filter(str.isdigit, response.text))
        if score_text:
            score = int(score_text)
            print(f"[3. AI 核心反馈] 实时情绪分值：{score}")

    except Exception as e:
        print(f"⚠️ [API 通道繁忙/连接失败] 已切换至本地算法。原因: {e}")
        score += random.randint(-5, 5)

    emotion = "快乐" if score > 70 else ("忧郁" if score < 40 else "平静")
    time.sleep(0.3)

    return jsonify({
        "score": score,
        "emotion": emotion,
        "status": "success"
    })


@app.route('/debug')
def debug_files():
    import glob
    models_path = os.path.join(STATIC_DIR, 'models')
    files = glob.glob(f"{models_path}/**/*.gltf", recursive=True)
    return jsonify({
        "static_folder_path": STATIC_DIR,
        "gltf_files_found": [f.replace(BASE_DIR, '') for f in files]
    })


# ==========================================
# 3. 自动诊断工具 (启动时检查文件夹)
# ==========================================
def run_startup_diagnosis():
    import glob
    print("\n" + "=" * 60)
    print("🔍 [自动诊断] 正在扫描你的 YVstatic 文件夹...")
    print(f"📁 目标扫描路径: {STATIC_DIR}\\models")

    models_path = os.path.join(STATIC_DIR, 'models')
    files = glob.glob(f"{models_path}/**/*.gltf", recursive=True)

    if not files:
        print("\n❌ 警告：没有找到任何 .gltf 模型文件！")
        print("   原因可能是：文件夹名字写错了，或者文件没有放到正确的位置。")
    else:
        print(f"\n✅ 成功找到了 {len(files)} 个模型文件。请核对它们的名字：")
        for f in files:
            # 统一把路径里的 \ 换成 /，方便对比前端代码
            rel_path = f.replace(BASE_DIR, '').replace('\\', '/')
            print(f"   ➡️  {rel_path}")

    print("=" * 60 + "\n")


# ==========================================
# 4. 启动引擎
# ==========================================

if __name__ == '__main__':
    run_startup_diagnosis()
    print("--- 情绪花园后端服务已启动 ---")
    print("本地访问地址: http://127.0.0.1:5000")
    app.run(debug=True, host='0.0.0.0', port=5000)