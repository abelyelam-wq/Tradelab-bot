import os
import yfinance as yf
import google.generativeai as genai
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, ContextTypes

genai.configure(api_key=os.environ.get("GEMINI_API_KEY"))

def get_super_pro_data(symbol="GC=F"):
    ticker = yf.Ticker(symbol)
    df = ticker.history(period="1mo", interval="1h")
    
    # ተጨማሪ አመልካቾች
    close = df['Close']
    sma20 = close.rolling(window=20).mean()
    std = close.rolling(window=20).std()
    upper_band = sma20 + (std * 2)
    lower_band = sma20 - (std * 2)
    
    # MACD ቀላል ስሌት
    ema12 = close.ewm(span=12).mean()
    ema26 = close.ewm(span=26).mean()
    macd = ema12 - ema26
    
    return f"ዋጋ: {close.iloc[-1]:.2f}, UpperBand: {upper_band.iloc[-1]:.2f}, LowerBand: {lower_band.iloc[-1]:.2f}, MACD: {macd.iloc[-1]:.4f}"

async def get_super_signal(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("🚀 የገበያውን ከፍተኛ የትንታኔ መረጃ በመተንተን ላይ ነኝ...")
    data = get_super_pro_data()
    
    prompt = f"""
    አንተ የዓለማችን ምርጥ የForex AI ትሬደር ነህ። መረጃው እነሆ: {data}
    
    በ Bollinger Bands እና በ MACD መሰረት ትንተናህን ስጥ። 
    ለተጠቃሚው የሚከተለውን ጥብቅ መረጃ አቅርብ፦
    1. BUY/SELL SIGNAL
    2. ENTRY (Price)
    3. STOP LOSS (SL) - ከ Bollinger Band ውጭ
    4. TAKE PROFIT (TP) - 1:3 Reward Ratio
    5. RISK MANAGEMENT: በዚህ ንግድ ላይ ምን ያህል ካፒታል መጠቀም እንዳለበት ምክር ስጥ (ለምሳሌ: 1-2% of account)
    6. ANALYSIS: በቴክኒክ ትንተና ላይ የተመሰረተ ጥልቅ ማብራሪያ።
    """
    
    model = genai.GenerativeModel('gemini-1.5-pro')
    response = model.generate_content(prompt)
    await update.message.reply_text(response.text, parse_mode='Markdown')

if __name__ == '__main__':
    app = ApplicationBuilder().token(os.environ.get("TELEGRAM_BOT_TOKEN")).build()
    app.add_handler(CommandHandler("signal", get_super_signal))
    app.run_polling()
