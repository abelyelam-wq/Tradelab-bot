import os
import yfinance as yf
import google.generativeai as genai
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, ContextTypes

# የ API ቁልፎችን ማዋቀር
genai.configure(api_key=os.environ.get("GEMINI_API_KEY"))

# የገበያ መረጃን በ real-time ለማምጣት (Yahoo Finance)
def get_market_analysis(symbol="GC=F"):
    ticker = yf.Ticker(symbol)
    data = ticker.history(period="1d", interval="15m")
    last_price = data['Close'].iloc[-1]
    return f"የአሁኑ ዋጋ: {last_price}፣ የገበያ ሁኔታ: የተረጋጋ።"

# ፕሮፌሽናል የሲግናል ተግባር
async def get_pro_signal(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("🔍 የገበያውን ጥልቅ መረጃ በመተንተን ላይ ነኝ፣ ትንሽ ጠብቅ...")
    
    market_data = get_market_analysis()
    
    prompt = f"""
    አንተ የላቀ የForex AI ትሬደር ነህ። እንደ ፕሮፌሽናል ትሬደር፣ በ SMC (Smart Money Concepts) በመጠቀም የሚከተለውን ተንትን፦
    
    1. MARKET CONTEXT: {market_data}
    2. TECHNICAL ANALYSIS: የገበያውን መዋቅር (Market Structure - BOS/CHoCH)፣ የOrder Blocks (OB) እና የFair Value Gaps (FVG) ቦታዎችን መርምር።
    
    ውሳኔህን በዚህ መልክ ብቻ ስጥ፦
    - SIGNAL: [BUY / SELL / HOLD]
    - CONFIDENCE: [Low / Medium / High]
    - ENTRY PRICE: [የዋጋ ነጥብ]
    - STOP LOSS (SL): [የመከላከያ ዋጋ]
    - TAKE PROFIT (TP): [የትርፍ ዋጋ - Risk/Reward 1:2]
    - ANALYSIS: የዚህን የንግድ ውሳኔ ምክንያት በትንሹ በሶስት ዓረፍተ ነገሮች በአማርኛ አስረዳ።
    """
    
    model = genai.GenerativeModel('gemini-1.5-pro')
    response = model.generate_content(prompt)
    
    await update.message.reply_text(response.text, parse_mode='Markdown')

if __name__ == '__main__':
    app = ApplicationBuilder().token(os.environ.get("TELEGRAM_BOT_TOKEN")).build()
    app.add_handler(CommandHandler("signal", get_pro_signal))
    print("ፕሮፌሽናል ትሬደር AI ተጀምሯል...")
    app.run_polling()

