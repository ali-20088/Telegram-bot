import os
from telegram import Update
from telegram.ext import (
    ApplicationBuilder,
    CommandHandler,
    MessageHandler,
    ContextTypes,
    filters
)
from sympy import *
from sympy.parsing.sympy_parser import (
    parse_expr,
    standard_transformations,
    implicit_multiplication_application,
    convert_xor
)
import logging

# Logger configuration
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

class MathBot:
    def __init__(self, token: str):
        self.app = ApplicationBuilder().token(token).build()
        self._setup_handlers()
        self.safe_dict = self._create_safe_dict()
        self.transformations = (
            standard_transformations +
            (implicit_multiplication_application, convert_xor)
        )

    def _create_safe_dict(self) -> dict:
        """Create a safe environment for mathematical operations"""
        symbols = symbols('x y z')
        constants = {
            'pi': pi,
            'E': E,
            'I': I,
            'oo': oo
        }
        functions = {
            'diff': diff,
            'integrate': integrate,
            'solve': solve,
            'simplify': simplify,
            'expand': expand,
            'factor': factor,
            'limit': limit,
            'series': series,
            'sin': sin, 'cos': cos, 'tan': tan,
            'sqrt': sqrt, 'log': log, 'exp': exp,
            'Matrix': Matrix, 'det': det,
            'Sum': Sum, 'Product': Product,
            'factorial': factorial, 'binomial': binomial,
            'Abs': Abs, 're': re, 'im': im
        }
        return {**dict(zip(['x', 'y', 'z'], symbols)), **constants, **functions}

    def _setup_handlers(self):
        """Setup Telegram handlers"""
        self.app.add_handler(CommandHandler("start", self.start))
        self.app.add_handler(MessageHandler(
            filters.TEXT & ~filters.COMMAND,
            self.handle_expression
        ))

    async def start(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Start command handler"""
        help_text = (
            "🔢 ربات محاسبات ریاضی پیشرفته\n\n"
            "📚 دستورات پشتیبانی شده:\n"
            "- محاسبات پایه: 2 + 3*4\n"
            "- مشتق: diff(x**2, x)\n"
            "- انتگرال: integrate(sin(x), (x, 0, pi))\n"
            "- حل معادله: solve(x**2 - 4, x)\n"
            "- ساده‌سازی: simplify((x**2 - 1)/(x - 1))\n"
            "- ماتریس: Matrix([[1, 2], [3, 4]])\n\n"
            "💡 مثال: (sqrt(16) + 2^3)*5"
        )
        await update.message.reply_text(help_text)

    async def handle_expression(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Process mathematical expressions"""
        user_input = update.message.text.strip()
        
        if not user_input:
            await update.message.reply_text("⚠️ لطفا یک عبارت ریاضی وارد کنید!")
            return

        try:
            result = self._process_expression(user_input)
            response = f"✅ نتیجه:\n`{result}`"
        except Exception as e:
            logger.error(f"Error processing {user_input}: {str(e)}")
            response = f"❌ خطا:\n`{str(e)}`"
        
        await update.message.reply_text(response, parse_mode="Markdown")

    def _process_expression(self, expr: str) -> str:
        """Core processing logic"""
        parsed_expr = parse_expr(
            expr,
            local_dict=self.safe_dict,
            transformations=self.transformations
        )
        
        if parsed_expr.is_Matrix:
            return pretty(parsed_expr, use_unicode=True)
            
        if parsed_expr.is_number:
            return f"N({parsed_expr}) = {parsed_expr.evalf(chop=True)}"
            
        return pretty(parsed_expr.doit(), use_unicode=True)

if __name__ == "__main__":
    bot = MathBot("7868707058:AAFpFiUUMfbNekf4_Ct2cT_v3wfdu7lL-JQ")
    logger.info("Bot is running...")
    bot.app.run_polling()
