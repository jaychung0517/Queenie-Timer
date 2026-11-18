import os
import json
import time
import base64
import random
from io import BytesIO
from datetime import datetime, timezone, timedelta
from PIL import Image
from google import genai
from google.genai import types

# ===== 基本設定 =====
TZ_TW = timezone(timedelta(hours=8))
ANIM_DIR = "animations"
JSON_PATH = "daily_animations.json"
NEW_SETS_PER_RUN = 2  # 早晚各新生成 2 組 (4 張/次 = 8 張/天 ≈ $8.06/月，穩低於 $10 額度)
TOTAL_SETS_IN_APP = 3  # 網頁維持顯示 3 組（第 3 組自動沿用上一輪精選）

IMAGE_MODELS = [
    "gemini-nano-banana-2.1",
    "gemini-3.1-flash-lite-image",
]

THREE_MODES = [
    "precure_pink", "zhongling_idol", "siren_mermaid", "teenieping_heart",
    "kuromi_rock", "cinnamoroll_fly", "kirby_dream", "pokemon_duo",
    "kanahei_duo", "sumikko_duo", "purin_party", "anya_magical",
]

# 鍾靈固定特徵（嚴格避開小小兵與冰雪奇緣/迪士尼系列）
ZHONGLING_BASE = (
    "an adorable 8-year-old East Asian girl with black twin pigtails, "
    "colorful star hair clips, and a pink wristwatch on her left wrist"
)

CHARACTER_THEMES = [
    {
        "tag_prefix": "三麗鷗櫻桃甜點共舞",
        "title": "🍒 鍾靈（櫻桃格紋烘焙裙）＆美樂蒂×彼安諾×帕恰狗 櫻桃奶油派對舞",
        "desc": "鍾靈換上「紅白櫻桃格紋烘焙洋裝＋立體紅櫻桃蝴蝶結髮箍」，與美樂蒂、粉紅小綿羊彼安諾、帕恰狗在馬卡龍蛋糕舞台跳愛心手勢舞！",
        "outfit": "wearing a red-and-white gingham cherry dress and a 3D red cherry bow headband",
        "stage": "a pastel cherry-cream bakery stage with giant macarons and floating musical notes",
        "partners": "My Melody in a pink hood, My Sweet Piano the fluffy pink sheep, and Pochacco the white puppy with black floppy ears",
    },
    {
        "tag_prefix": "奇妙萌可皇家遊行舞",
        "title": "💖 鍾靈（蜜桃金皇家樂隊服）＆愛心萌可×幸運萌可 星光遊行舞",
        "desc": "鍾靈穿上「蜜桃粉金星光皇家小樂隊制服裙＋羽毛小禮帽」，與韓國超人氣《奇妙萌可》愛心萌可、幸運萌可揮舞金星指揮棒大遊行！",
        "outfit": "wearing a peach-pink and gold royal marching band uniform skirt with a tiny feathered mini top hat",
        "stage": "a sparkling starlight royal parade stage with pastel rainbow arches",
        "partners": "Heartsping (a small big-headed pastel-pink fairy creature with huge sparkling magenta-pink anime eyes, a curled hot-pink bangs tuft on its forehead, two big fluffy pastel-pink twin-tails with curled hot-pink tips held by sparkly pink heart hair clips and a tiny silver tiara, wearing a cute pink-and-white ruffled dress with a golden crown emblem on the chest) and a cute mint-green four-leaf clover fairy mascot",
    },
    {
        "tag_prefix": "人魚賽蓮珊瑚泡泡舞",
        "title": "🧜‍♀️ 鍾靈（薰衣草紫貝殼裙）＆人魚賽蓮×吉伊×海獺師傅 珊瑚泡泡舞",
        "desc": "鍾靈換上「薰衣草紫粉貝殼荷葉小浴衣裙＋珍珠星星髮夾」，與正版造型人魚賽蓮、吉伊卡哇、海獺師傅在星光珊瑚海開泡泡派對！",
        "outfit": "wearing a lavender-purple and pink seashell ruffle dress and pearl star hair clips",
        "stage": "a glowing pastel underwater coral reef stage with giant pearl shells and rainbow bubbles",
        "partners": "the official Nagano Chiikawa movie Siren character (a chubby round kawaii white Chiikawa-style siren creature with a black widow's peak marking on its forehead, two black scalloped heart-shaped ears with coral-orange inner ears, cute omega mouth with two short whisker lines on each cheek, white chubby arms, and a plump coral-orange scaled mermaid tail with a light-pink waist band), small white round Chiikawa wearing a flower crown, and Rakko the cute tan sea otter hero with a small cape",
    },
    {
        "tag_prefix": "三麗鷗雲端熱氣球共舞",
        "title": "🎈 鍾靈（天藍雲朵吊帶裙）＆大耳狗×人魚漢頓×雙子星 雲端熱氣球舞",
        "desc": "鍾靈換上「天藍雲朵氣球蓬蓬吊帶裙＋立體大耳狗蝴蝶結髮箍」，與大耳狗喜拿、人魚漢頓、雙子星在彩虹熱氣球雲海跳飛翔舞！",
        "outfit": "wearing a sky-blue puffy cloud suspender dress and a 3D Cinnamoroll white puppy-ear bow headband",
        "stage": "a pastel sky-blue cloud stage with rainbow hot-air balloons and golden sunbeams",
        "partners": "Cinnamoroll the white puppy with long floppy ears, Hangyodon the cute teal-blue fish-man mascot, and Little Twin Stars chibi fairies with pastel blue and pink hair",
    },
    {
        "tag_prefix": "酷洛米＆布丁狗搖滾共舞",
        "title": "🎸 鍾靈（紫黑甜酷格紋裙）＆酷洛米×布丁狗 星光搖滾甜點演唱會舞",
        "desc": "鍾靈換上「紫黑甜酷龐克格紋百褶裙＋酷洛米小惡魔耳朵蝴蝶結髮箍」，與酷洛米、布丁狗在焦糖布丁霓虹舞台手拿星星麥克風熱力搖滾共舞！",
        "outfit": "wearing a sweet-punk purple-and-black plaid pleated skirt outfit and a 3D Kuromi jester-ear bow headband",
        "stage": "a neon pastel purple-and-gold dessert rock concert stage with giant caramel puddings and glowing star speakers",
        "partners": "Kuromi in her black jester hat with a pink skull and Pompompurin the chubby golden retriever puppy in a brown beret",
    },
    {
        "tag_prefix": "寶可夢＆星之卡比共舞",
        "title": "🎀 鍾靈（粉藍馬卡龍精靈裙）＆仙子伊布×星之卡比×波加曼 彩虹音樂舞",
        "desc": "鍾靈穿上「粉藍夢幻馬卡龍精靈訓練家禮服＋蝴蝶結緞帶髮夾」，與仙子伊布、星之卡比、波加曼搖動星光手鼓跳彩虹音樂派對舞！",
        "outfit": "wearing a pastel pink-and-blue macaron fairy trainer dress and pink-and-blue ribbon hair clips",
        "stage": "a pastel rainbow dreamland music stage with floating candy stars and musical notes",
        "partners": "a cute pink-and-cream ribbon fox fairy mascot with blue eyes, a cute round pink puffball creature with red shoes, and a cute little blue penguin mascot",
    },
    {
        "tag_prefix": "芙莉蓮＆安妮亞花田共舞",
        "title": "💠 鍾靈（薄荷綠金星魔法披風）＆Q版芙莉蓮×安妮亞×彭德 花田魔法舞",
        "desc": "鍾靈穿上「薄荷綠金星魔法學園披風制服＋閃亮蝴蝶結高筒靴」，與 Q 版芙莉蓮、安妮亞及大白狗彭德在發光藍月花田揮動水晶花杖共舞！",
        "outfit": "wearing a mint-green and gold star magic academy cape uniform skirt with white ribbon boots",
        "stage": "a glowing blue-petal flower field stage under a pastel rainbow sky",
        "partners": "a cute 3D chibi silver-twin-tailed elf mage girl in white-and-gold cape, a cute pink-haired chibi anime girl with two black horn hair buns wearing a black-and-gold school dress, and a big fluffy white dog with black paws",
    },
    {
        "tag_prefix": "角落小夥伴＆卡娜赫拉野餐舞",
        "title": "🍓 鍾靈（草莓奶油圍裙裙）＆角落小夥伴×卡娜赫拉 草莓野餐派對舞",
        "desc": "鍾靈換上「草莓奶油點點小圍裙洋裝＋毛絨兔耳髮箍」，與角落小夥伴、卡娜赫拉粉紅兔兔與 P 助在草莓草地野餐舞台開心共舞！",
        "outfit": "wearing a strawberry-cream polka-dot apron dress and a fluffy bunny ear headband",
        "stage": "a sunny pastel strawberry meadow picnic stage with giant shortcakes and floating hearts",
        "partners": "Sumikko Gurashi cute round pastel polar bear, cat, and lizard mascots, plus Kanahei's chubby pink rabbit and tiny white chick",
    },
]


def build_frame_prompts(theme: dict) -> tuple[str, str]:
    common = (
        f"Wide-angle full-body 3D kawaii Pixar and anime style animation frame on {theme['stage']}. "
        f"In the center, {ZHONGLING_BASE}, {theme['outfit']}. "
        f"Dancing beside her are {theme['partners']}. "
        f"Bright kawaii 3D lighting, full characters visible with wide margin."
    )
    frame_a = f"{common} Everyone is smiling brightly, jumping Left-Up and making cute heart gestures in synchronized joy."
    frame_b = f"{common} Everyone is laughing happily, leaning Right-Up, spinning and waving star wands with colorful confetti."
    return frame_a, frame_b


def generate_image_bytes(client: genai.Client, prompt: str) -> bytes:
    last_error = None
    for model_name in IMAGE_MODELS:
        try:
            print(f"Generating image with {model_name}...")
            resp = client.models.generate_content(
                model=model_name,
                contents=prompt,
                config=types.GenerateContentConfig(
                    response_modalities=["IMAGE"],
                    image_config=types.ImageConfig(aspect_ratio="4:3"),
                ),
            )
            for candidate in getattr(resp, "candidates", []) or []:
                for part in getattr(candidate.content, "parts", []) or []:
                    inline = getattr(part, "inline_data", None)
                    if inline and getattr(inline, "data", None):
                        data = inline.data
                        if isinstance(data, str):
                            return base64.b64decode(data)
                        return data
            raise RuntimeError(f"{model_name} returned no image bytes")
        except Exception as e:
            print(f"Model {model_name} failed: {e}")
            last_error = e
            time.sleep(2)
    raise RuntimeError(f"All image models failed. Last error: {last_error}")


def save_jpeg(raw_bytes: bytes, out_path: str) -> None:
    img = Image.open(BytesIO(raw_bytes)).convert("RGB")
    img.save(out_path, format="JPEG", quality=88, optimize=True)


def load_previous_json() -> dict:
    if os.path.exists(JSON_PATH):
        try:
            with open(JSON_PATH, "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception:
            pass
    return {}


def main():
    api_key = os.environ.get("GEMINI_API_KEY", "").strip()
    if not api_key:
        raise RuntimeError("Missing GEMINI_API_KEY environment variable")

    os.makedirs(ANIM_DIR, exist_ok=True)
    client = genai.Client(api_key=api_key)

    now_tw = datetime.now(TZ_TW)
    slot_period = "AM" if now_tw.hour < 12 else "PM"
    slot_key = f"{now_tw.strftime('%Y-%m-%d')}-{slot_period}"
    slot_label = "早安更新" if slot_period == "AM" else "晚間更新"
    file_prefix = f"starry_{now_tw.strftime('%Y%m%d')}_{slot_period.lower()}"

    prev_data = load_previous_json()
    prev_anims = prev_data.get("animations", [])
    prev_titles = {a.get("title", "") for a in prev_anims}

    # 挑選與上一輪不重複的主題
    available_themes = [t for t in CHARACTER_THEMES if t["title"] not in prev_titles]
    if len(available_themes) < NEW_SETS_PER_RUN:
        available_themes = CHARACTER_THEMES[:]
    random.shuffle(available_themes)

    # 若倉庫裡還沒有舊動畫，首次先補滿 3 組；之後每次只新生成 2 組（4 張圖）
    num_to_generate = NEW_SETS_PER_RUN if len(prev_anims) >= 1 else TOTAL_SETS_IN_APP
    chosen_themes = available_themes[:num_to_generate]

    new_anims = []
    for idx, theme in enumerate(chosen_themes, start=1):
        prompt_a, prompt_b = build_frame_prompts(theme)
        raw_a = generate_image_bytes(client, prompt_a)
        time.sleep(2)
        raw_b = generate_image_bytes(client, prompt_b)
        time.sleep(2)

        path_a = f"{ANIM_DIR}/{file_prefix}_anim{idx}_frameA.jpg"
        path_b = f"{ANIM_DIR}/{file_prefix}_anim{idx}_frameB.jpg"
        save_jpeg(raw_a, path_a)
        save_jpeg(raw_b, path_b)

        new_anims.append({
            "title": theme["title"],
            "desc": theme["desc"],
            "tag": f"✨ {now_tw.strftime('%m/%d')} {slot_label} {idx}｜{theme['tag_prefix']}",
            "frameA": path_a,
            "frameB": path_b,
        })

    # 第 3 組沿用上一輪第 1 組精選動畫，維持 3 組完整輪播
    while len(new_anims) < TOTAL_SETS_IN_APP and prev_anims:
        carry = dict(prev_anims[0])
        new_anims.append(carry)

    # 清理過舊的圖檔（只保留目前 daily_animations.json 會用到的檔案）
    active_files = set()
    for a in new_anims:
        if a.get("frameA"):
            active_files.add(os.path.basename(a["frameA"]))
        if a.get("frameB"):
            active_files.add(os.path.basename(a["frameB"]))
    for fname in os.listdir(ANIM_DIR):
        if fname.endswith(".jpg") and fname not in active_files:
            try:
                os.remove(os.path.join(ANIM_DIR, fname))
            except Exception:
                pass

    modes = random.sample(THREE_MODES, 2)
    output = {
        "slot_key": slot_key,
        "updated_at": now_tw.strftime("%Y-%m-%d %H:%M"),
        "three_mode_1": modes[0],
        "three_mode_2": modes[1],
        "song_idx": random.randint(0, 3),
        "animations": new_anims,
    }

    with open(JSON_PATH, "w", encoding="utf-8") as f:
        json.dump(output, f, ensure_ascii=False, indent=2)

    print(f"Successfully updated {slot_key} with {len(chosen_themes)} new sets ({len(chosen_themes)*2} new images).")


if __name__ == "__main__":
    main()
