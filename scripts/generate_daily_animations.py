import datetime
import io
import json
import os
import random
from PIL import Image
from google import genai
from google.genai import types

API_KEY = os.environ.get("GEMINI_API_KEY")
if not API_KEY:
    raise RuntimeError("找不到 GEMINI_API_KEY！請到 GitHub Repository Settings -> Secrets and variables -> Actions 新增 GEMINI_API_KEY。")

client = genai.Client(api_key=API_KEY)

tw_now = datetime.datetime.now(datetime.timezone(datetime.timedelta(hours=8)))
slot_period = "AM" if tw_now.hour < 12 else "PM"
slot_key = tw_now.strftime("%Y-%m-%d") + "-" + slot_period
updated_at = tw_now.strftime("%Y-%m-%d %H:%M")

IP_THEMES = [
    {
        "key": "siren_mermaid",
        "ip_name": "吉伊卡哇人魚島「人魚賽蓮」",
        "outfit_zh": "珍珠貝殼人魚公主澎澎裙＋海星髮夾",
        "scene_zh": "星光珊瑚礁海島舞台",
        "three_mode": "siren_mermaid",
        "outfit_en": "dreamy iridescent pearl-pink and aqua seashell ruffle princess dress with seashell and star hair clips",
        "scene_en": "glowing pastel coral reef island beach stage under a starry tropical sky with rainbow bubbles",
        "chars_en": "a large, chubby, round, kawaii Nagano-style siren creature with a round pure-white upper body and round white face, a prominent black widow-peak fur marking on the center of its forehead pointing down between its eyes, two scalloped black heart-shaped ears with coral-orange inner ears on top of its head, two short whisker lines on each cheek, a cute cat-like omega mouth, short chubby white arms, and a plump rounded coral-orange scaled mermaid fishtail lower body with a light-pink waist band, plus two small chubby white and blue kawaii island mascot friends wearing green leaf skirts"
    },
    {
        "key": "teenieping_heart",
        "ip_name": "韓國《奇妙萌可》愛心萌可＆閃耀萌可",
        "outfit_zh": "鑽石愛心粉白蕾絲公主裙＋小銀皇冠",
        "scene_zh": "粉紅水晶愛心城堡舞廳",
        "three_mode": "teenieping_heart",
        "outfit_en": "dreamy pastel pink-and-white diamond-heart ruffled princess dress with a tiny silver heart tiara and star hair clips",
        "scene_en": "glowing pastel pink crystal castle ballroom filled with floating glowing hearts and golden stars",
        "chars_en": "a tiny cute 3D Korean chibi fairy mascot with huge sparkling magenta-pink anime eyes, a curled hot-pink bangs tuft on its forehead, two big fluffy pastel-pink twin-tails with curled hot-pink tips held by sparkly pink heart hair clips and a tiny silver tiara, wearing a pink-and-white ruffled dress with a golden crown emblem on the chest, plus a tiny pastel-blue chibi fairy mascot with star hair clips"
    },
    {
        "key": "kuromi_melody",
        "ip_name": "《三麗鷗》酷洛米＆美樂蒂",
        "outfit_zh": "紫黑格紋甜酷搖滾蕾絲短裙＋蝴蝶結髮箍",
        "scene_zh": "霓虹糖果城堡演唱會舞台",
        "three_mode": "kuromi_rock",
        "outfit_en": "sweet-cool pastel purple-and-black plaid lace rocker dress with a purple-and-black bow headband and star hair clips",
        "scene_en": "glowing neon candy castle concert stage with colorful spotlights and pastel lollipops",
        "chars_en": "a cute white bunny mascot wearing a black jester hood with pointed ears and a pink skull mark on the forehead, and a cute white bunny mascot wearing a pastel-pink hood with a white flower on it"
    },
    {
        "key": "pokemon_cheer",
        "ip_name": "《精靈寶可夢》皮卡丘＆仙子伊布",
        "outfit_zh": "薄荷綠格紋精靈學園披肩百褶裙",
        "scene_zh": "陽光向日葵彩虹舞台",
        "three_mode": "pokemon_duo",
        "outfit_en": "fresh pastel mint-green and cream plaid capelet school uniform dress with four-leaf clover and star hair clips",
        "scene_en": "sunny morning sunflower garden concert stage with a bright rainbow arch",
        "chars_en": "a cute pastel-pink and cream fox-like fairy creature with long flowing ribbon-like bows and big blue eyes, and a chubby bright-yellow mouse-like creature with rosy red cheeks and lightning-bolt tail wearing a tiny flower crown"
    },
    {
        "key": "kanahei_bakery",
        "ip_name": "《卡娜赫拉的小動物》粉紅兔兔＆白鳥P助",
        "outfit_zh": "焦糖格紋學院百褶裙＋草莓吐司斜背包",
        "scene_zh": "陽光草莓甜點烘焙坊",
        "three_mode": "kanahei_duo",
        "outfit_en": "caramel-plaid pleated school uniform skirt with a cream cardigan, red ribbon bow tie, and a cute strawberry-toast crossbody bag",
        "scene_en": "sunny pastel morning bakery patisserie stage with giant strawberry pancakes and macarons",
        "chars_en": "a chubby round pastel-pink bunny mascot with rosy cheeks wearing a tiny white chef hat, and a tiny round chubby white bird mascot with a small yellow beak and pink cheeks balancing a mini bread roll on its head"
    },
    {
        "key": "cinnamoroll_twinstars",
        "ip_name": "《三麗鷗》大耳狗喜拿＆雙子星",
        "outfit_zh": "粉藍粉紅漸層星光雲朵澎澎洋裝＋星星睡帽",
        "scene_zh": "棉花糖流星銀河雲端舞台",
        "three_mode": "cinnamoroll_fly",
        "outfit_en": "dreamy pastel sky-blue and rose-pink gradient cloud puff dress with a cute pastel star nightcap hat",
        "scene_en": "glowing cotton-candy cloud stage under a starry crescent moon sky with shooting stars",
        "chars_en": "a cute chubby white puppy mascot with super long floppy ears, a cute chibi little star-boy angel with pastel blue hair carrying a golden star, and a cute chibi little star-girl angel with long pastel pink hair holding a star wand"
    },
    {
        "key": "sumikko_cafe",
        "ip_name": "《角落小夥伴》白熊＆炸蝦尾＆企鵝",
        "outfit_zh": "粉黃格紋陽光早午餐荷葉洋裝",
        "scene_zh": "花園蜂蜜鬆餅派對廣場",
        "three_mode": "sumikko_duo",
        "outfit_en": "cheerful pastel yellow-and-pink ruffle brunch pinafore dress with strawberry ribbon hair clips",
        "scene_en": "sunny pastel garden cafe plaza with a giant honey waffle platter and colorful flowers",
        "chars_en": "a chubby round shy white polar bear mascot wrapped in a pink polka-dot cloth, a tiny golden fried-shrimp-tail mascot wearing a pink bow, and a cute pastel-green penguin mascot"
    },
    {
        "key": "anya_bond",
        "ip_name": "《間諜家家酒》安妮亞＆彭德大白狗",
        "outfit_zh": "伊甸學園黑金滾邊公主小禮服",
        "scene_zh": "星光氣球城堡派對大廳",
        "three_mode": "anya_magical",
        "outfit_en": "cute black-and-gold trim academy princess dress with colorful star hair clips",
        "scene_en": "pastel party palace hall filled with floating pastel balloons and confetti",
        "chars_en": "a cute little chibi girl with pastel-pink hair and two black horn hair-cones on her head, and a big fluffy white dog with dark paws and a black bow tie"
    },
    {
        "key": "labubu_puppy",
        "ip_name": "泡泡瑪特粉紅 Labubu ＆馬爾濟斯線條小狗",
        "outfit_zh": "粉紫雲朵吊帶裙＋兔耳毛絨貝雷帽",
        "scene_zh": "夢幻旋轉木馬遊樂園",
        "three_mode": "purin_party",
        "outfit_en": "pastel lavender-and-pink fluffy cloud overall dress with a cute bunny-ear beret hat",
        "scene_en": "dreamy pastel carousel amusement park with glowing fairy lights",
        "chars_en": "a cute fluffy pastel-pink monster elf character with long bunny ears and a mischievous cute grin, plus a chubby fluffy white Maltese puppy and a cute golden retriever puppy"
    },
    {
        "key": "sakura_magic",
        "ip_name": "《庫洛魔法使》飛翼小可＆星光斯比",
        "outfit_zh": "櫻花小天使翅膀魔法使禮服＋粉紅貝雷帽",
        "scene_zh": "金色星光櫻花魔法陣舞台",
        "three_mode": "precure_pink",
        "outfit_en": "dreamy pastel cherry-blossom pink and white frilly magical girl dress with small white angel wings and a cute pink beret hat",
        "scene_en": "glowing golden star magic circle stage with swirling cherry blossom petals",
        "chars_en": "a cute chubby golden-yellow plush lion cub mascot with small white angel wings on its back, and a cute small dark-blue winged cat mascot with a golden moon mark"
    }
]

JSON_PATH = "daily_animations.json"
used_history = []
if os.path.exists(JSON_PATH):
    try:
        with open(JSON_PATH, "r", encoding="utf-8") as f:
            prev_data = json.load(f)
            used_history = prev_data.get("used_keys", [])
    except Exception:
        used_history = []

recent_keys = set(used_history[-6:])
candidates = [t for t in IP_THEMES if t["key"] not in recent_keys]
if len(candidates) < 3:
    candidates = IP_THEMES[:]

random.shuffle(candidates)
selected = candidates[:3]


def generate_image_bytes(prompt_text: str) -> bytes:
    for model_name in ["imagen-3.0-generate-002", "imagen-4.0-generate-001"]:
        try:
            res = client.models.generate_images(
                model=model_name,
                prompt=prompt_text,
                config=types.GenerateImagesConfig(
                    number_of_images=1,
                    aspect_ratio="4:3",
                    output_mime_type="image/jpeg",
                ),
            )
            if res.generated_images:
                return res.generated_images[0].image.image_bytes
        except Exception as e:
            print(f"Model {model_name} fallback check: {e}")

    resp = client.models.generate_content(
        model="gemini-2.5-flash-image",
        contents=prompt_text,
        config=types.GenerateContentConfig(response_modalities=["IMAGE"]),
    )
    for part in resp.candidates[0].content.parts:
        if part.inline_data and part.inline_data.data:
            return part.inline_data.data
    raise RuntimeError("所有影像生成模型皆未回傳圖片")


os.makedirs("animations", exist_ok=True)
animations_out = []

for idx, theme in enumerate(selected, start=1):
    base_girl = (
        "An adorable 8-year-old East Asian girl (Zhong Ling) with black twin pigtails, "
        "colorful hair clips, a pink wristwatch on her left wrist, wearing a "
        f"{theme['outfit_en']} and white clogs, standing center stage at a {theme['scene_en']}."
    )
    prompt_a = (
        f"Wide-angle full-body 3D Pixar and Sanrio kawaii animation frame: {base_girl} "
        f"Beside her are {theme['chars_en']}. "
        "Pose 1: Zhong Ling smiles brightly with sparkling starry eyes making a cute peace V-sign "
        "while her adorable companions wave cheerfully. Wide-angle full-body view, no text."
    )
    prompt_b = (
        f"Wide-angle full-body 3D Pixar and Sanrio kawaii animation frame: {base_girl} "
        f"Beside her are {theme['chars_en']}. "
        "Pose 2: Zhong Ling winks one eye playfully and leaps high into the air forming a big heart "
        "over her head with both hands, while all companions jump high into the air cheering amidst "
        "sparkling stars and musical notes. Wide-angle full-body view, no text."
    )

    file_a = f"animations/anim{idx}_a.jpg"
    file_b = f"animations/anim{idx}_b.jpg"

    for p_text, out_file in [(prompt_a, file_a), (prompt_b, file_b)]:
        raw_bytes = generate_image_bytes(p_text)
        im = Image.open(io.BytesIO(raw_bytes)).convert("RGB")
        im.thumbnail((800, 600), Image.Resampling.LANCZOS)
        im.save(out_file, format="JPEG", quality=82, optimize=True)
        print(f"Saved {out_file}")

    animations_out.append({
        "title": f"{idx}. 鍾靈（{theme['outfit_zh']}）＆{theme['ip_name']}共舞",
        "tag": f"🎬 {tw_now.strftime('%m/%d')} {'早晨' if slot_period == 'AM' else '傍晚'}主打 {idx}：{theme['ip_name']}",
        "caption": f"【{updated_at} 全自動新生成】鍾靈換上「{theme['outfit_zh']}」，在{theme['scene_zh']}與「{theme['ip_name']}」比 YA 微笑 ➔ 俏皮眨眼跳起比出大愛心！",
        "frameA": f"./{file_a}",
        "frameB": f"./{file_b}",
    })

new_history = (used_history + [t["key"] for t in selected])[-18:]
output_payload = {
    "slot_key": slot_key,
    "updated_at": updated_at,
    "three_mode_1": selected[0]["three_mode"],
    "three_mode_2": selected[1]["three_mode"],
    "used_keys": new_history,
    "animations": animations_out,
}

with open(JSON_PATH, "w", encoding="utf-8") as f:
    json.dump(output_payload, f, ensure_ascii=False, indent=2)

print("Successfully generated 6 animations and updated daily_animations.json:", slot_key)
