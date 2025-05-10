from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, ContextTypes, filters
from sympy import *
from sympy.parsing.sympy_parser import parse_expr

# تعریف متغیرها
x, y, z = symbols('x y z')
init_printing(use_unicode=True)

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "سلام! من یک ربات محاسبات ریاضی هستم.\n"
        "میتونی مواردی مثل اینا رو بفرستی:\n"
        "`2 + 3 * 4`\n"
        "`diff(x**2, x)`\n"
        "`solve(x**2 - 4, x)`\n"
        "`integrate(sin(x), x)`",
        parse_mode="Markdown"
    )

async def calculate(update: Update, context: ContextTypes.DEFAULT_TYPE):
    expr = update.message.text.strip()

    try:
        result = eval(expr, {"__builtins__": {}}, {
            "x": x, "y": y, "z": z,
            "diff": diff,
            "integrate": integrate,
            "solve": solve,
            "simplify": simplify,
            "expand": expand,
            "factor": factor,
            "limit": limit,
            "sin": sin, "cos": cos, "tan": tan,
            "ln": ln, "log": log, "pi": pi, "E": E,
        })
        await update.message.reply_text(f"`{expr}` = `{result}`", parse_mode="Markdown")
    except Exception as e:
        await update.message.reply_text(f"خطا: `{e}`", parse_mode="Markdown")

# اینجا توکن بات شما وارد شده (فقط برای تست! بعداً تغییرش بده)
app = ApplicationBuilder().token("7868707058:AAFpFiUUMfbNekf4_Ct2cT_v3wfdu7lL-JQ").build()

app.add_handler(CommandHandler("start", start))
app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, calculate))

app.run_polling()
