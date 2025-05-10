import os
from telegram import Update
from telegram.ext import (
    ApplicationBuilder,
    CommandHandler,
    MessageHandler,
    ContextTypes,
    filters
)
from sympy import (
    symbols, diff, integrate, solve, simplify, expand, factor, limit,
    sin, cos, tan, sqrt, log, exp, pi, E, I, oo, Matrix, det, Sum,
    Product, factorial, binomial, Abs, re, im, series, pretty, Eq, N
)
from sympy.parsing.sympy_parser import (
    parse_expr,
    standard_transformations,
    implicit_multiplication_application,
    convert_xor
)
import logging
import re

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
        sym_x, sym_y, sym_z = symbols('x y z')
        
        return {
            'x': sym_x, 'y': sym_y, 'z': sym_z,
            'pi': pi, 'E': E, 'I': I, 'oo': oo,
            'diff': diff, 'integrate': integrate, 'solve': solve,
            'simplify': simplify, 'expand': expand, 'factor': factor,
            'limit': limit, 'series': series, 'Eq': Eq, 'N': N,
            'sin': sin, 'cos': cos, 'tan': tan, 'sqrt': sqrt,
            'log': log, 'exp': exp, 'Matrix': Matrix, 'det': det,
            'Sum': Sum, 'Product': Product, 'factorial': factorial,
            'binomial': binomial, 'Abs': Abs, 're': re, 'im': im
        }

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
            "💡 هر خط یک دستور مستقل است\n"
            "💡 برای توان از ** یا ^ استفاده کنید"
        )
        await update.message.reply_text(help_text)

    async def handle_expression(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Process mathematical expressions"""
        user_input = update.message.text.strip()
        
        if not user_input:
            await update.message.reply_text("⚠️ لطفا یک عبارت ریاضی وارد کنید!")
            return

        try:
            # پردازش خط به خط
            results = []
            for line in user_input.split('\n'):
                line = line.strip()
                if line:
                    try:
                        result = self._process_single_expression(line)
                        results.append(f"`{line}` = `{result}`")
                    except Exception as e:
                        results.append(f"`{line}` ❌ خطا: `{str(e)}`")
            
            response = "📝 نتایج:\n" + "\n\n".join(results)
        except Exception as e:
            logger.error(f"Error processing {user_input}: {str(e)}")
            response = f"❌ خطای کلی:\n`{str(e)}`"
        
        await update.message.reply_text(response, parse_mode="Markdown")

    def _process_single_expression(self, expr: str) -> str:
        """Process a single mathematical expression"""
        # تبدیل ^ به ** و رفع فاصله‌های نامناسب
        expr = self._preprocess_expression(expr)
        
        parsed_expr = parse_expr(
            expr,
            local_dict=self.safe_dict,
            transformations=self.transformations
        )
        
        if hasattr(parsed_expr, 'is_Matrix') and parsed_expr.is_Matrix:
            return pretty(parsed_expr, use_unicode=True)
            
        if hasattr(parsed_expr, 'is_number') and parsed_expr.is_number:
            return str(parsed_expr.evalf(chop=True))
            
        if isinstance(parsed_expr, list):
            return pretty(parsed_expr, use_unicode=True)
            
        return pretty(parsed_expr.doit(), use_unicode=True)

    def _preprocess_expression(self, expr: str) -> str:
        """Preprocess the expression before parsing"""
        # جایگزینی ^ با **
        expr = expr.replace('^', '**')
        # حذف فاصله‌های اضافی حول عملگرها
        expr = re.sub(r'\s*([+\-*/])\s*', r' \1 ', expr)
        return expr.strip()

if __name__ == "__main__":
    bot = MathBot("7868707058:AAFpFiUUMfbNekf4_Ct2cT_v3wfdu7lL-JQ")
    logger.info("Bot is running...")
    bot.app.run_polling()
