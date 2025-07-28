import logging
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, ContextTypes, filters
from config import load_config
from github_api import GitHubManager
from domain_parser import extract_domain

config = load_config()
g = GitHubManager(config['github_token'], config['github']['repo'], config['github']['branch'])

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("发送域名或URL以添加至规则列表。")

async def handle(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    if user_id not in config['allowed_users']:
        return

    text = update.message.text.strip()
    domain = extract_domain(text)
    if not domain:
        await update.message.reply_text("⚠ 无法识别有效域名。")
        return

    clash_rule = f"  - DOMAIN-SUFFIX,{domain}"
    loon_rule = f"DOMAIN-SUFFIX,{domain}"

    # Clash 添加逻辑
    clash_lines, clash_sha = g.read_file(config['github']['clash_rule_path'])
    if clash_rule not in clash_lines:
        clash_lines.append(clash_rule)
        url1 = g.write_file(config['github']['clash_rule_path'], clash_lines, clash_sha, f"Add {domain}")
        msg1 = f"✅ Clash 规则已添加\n[查看提交]({url1})"
    else:
        msg1 = "⚠ Clash 规则中已存在"

    # Loon 添加逻辑
    loon_lines, loon_sha = g.read_file(config['github']['loon_rule_path'])
    if loon_rule not in loon_lines:
        loon_lines.append(loon_rule)
        url2 = g.write_file(config['github']['loon_rule_path'], loon_lines, loon_sha, f"Add {domain}")
        msg2 = f"✅ Loon 规则已添加\n[查看提交]({url2})"
    else:
        msg2 = "⚠ Loon 规则中已存在"

    await update.message.reply_text(f"识别到域名：`{domain}`\n\n{msg1}\n{msg2}", parse_mode='Markdown')

def main():
    logging.basicConfig(level=logging.INFO)
    app = ApplicationBuilder().token(config['telegram_token']).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(filters.TEXT & (~filters.COMMAND), handle))
    app.run_polling()

if __name__ == "__main__":
    main()
