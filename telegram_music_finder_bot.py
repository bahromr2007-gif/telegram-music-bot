import os
import yt_dlp
import instaloader
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, ContextTypes, filters

# 🔑 Tokeningni shu yerga yoz
TELEGRAM_TOKEN = "8226993737:AAErIjCoq80NhvBsXr0nMbMMKWLBXSoaAD4"

# /start komandasi
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("🎵 Salom! Men SongFastBot'ga o‘xshagan botman.\n"
                                    "Menga musiqa nomi, YouTube yoki Instagram link tashla 🎧")

# 🔗 Instagram video yuklash
async def download_instagram(link, file_name):
    loader = instaloader.Instaloader(dirname_pattern='.', filename_pattern=file_name, save_metadata=False)
    try:
        loader.download_post(instaloader.Post.from_shortcode(loader.context, link.split("/")[-2]), target='.')
        return True
    except Exception as e:
        print(e)
        return False

# 🧩 Asosiy xabarlar
async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = update.message.text.strip()

    # YouTube link bo‘lsa
    if "youtube.com" in text or "youtu.be" in text:
        await update.message.reply_text("⏳ Yuklanmoqda...")

        ydl_opts = {
            "format": "bestaudio/best",
            "outtmpl": "song.mp3",
            "quiet": True,
        }

        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            ydl.download([text])

        await update.message.reply_audio(audio=open("song.mp3", "rb"))
        os.remove("song.mp3")
        return

    # Instagram link bo‘lsa
    elif "instagram.com" in text:
        await update.message.reply_text("📥 Instagram videosi yuklanmoqda...")

        if await download_instagram(text, "insta_video"):
            for file in os.listdir("."):
                if file.endswith(".mp4"):
                    await update.message.reply_video(video=open(file, "rb"))
                    os.remove(file)
        else:
            await update.message.reply_text("⚠️ Videoni yuklab bo‘lmadi.")
        return

    # Oddiy so‘rov bo‘lsa — YouTube’da qidirish
    else:
        await update.message.reply_text(f"🔎 '{text}' musiqasini qidirayapman...")

        search_url = f"ytsearch1:{text}"
        ydl_opts = {
            "format": "bestaudio/best",
            "outtmpl": "result.mp3",
            "quiet": True,
        }

        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(search_url, download=True)
            title = info['entries'][0]['title']

        await update.message.reply_audio(audio=open("result.mp3", "rb"), caption=f"🎶 {title}")
        os.remove("result.mp3")

# 🔧 Botni ishga tushurish
app = ApplicationBuilder().token(TELEGRAM_TOKEN).build()
app.add_handler(CommandHandler("start", start))
app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))

print("🤖 Bot ishlayapti...")
app.run_polling()
