import logging
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, ContextTypes, filters
from config import load_config
from github_api import GitHubManager
from domain_parser import extract_domain

config = load_config()
g = GitHubManager(config['github_token'], config['github']['repo'], config['github']['branch'])

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("发送域名或URL以添加至规则列表，或使用 /query <域名> 查询。")

async def query(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not context.args:
        await update.message.reply_text("请提供一个域名进行查询。用法: /query <域名>")
        return

    domain = extract_domain(context.args[0])
    if not domain:
        await update.message.reply_text("⚠ 无法识别有效域名。")
        return

    clash_exists = g.check_domain_exists(config['github']['clash_rule_path'], domain)
    loon_exists = g.check_domain_exists(config['github']['loon_rule_path'], domain)

    msg1 = f"- Clash 规则: {'✅' if clash_exists else '❌'}"
    msg2 = f"- Loon 规则: {'✅' if loon_exists else '❌'}"

    await update.message.reply_text(f"查询结果 for `{domain}`:\n{msg1}\n{msg2}", parse_mode='Markdown')

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
    commit_message = f"Add {domain}"

    # Clash 添加逻辑
    clash_url, clash_status = g.add_rule_to_file(config['github']['clash_rule_path'], clash_rule, commit_message)
    if clash_status == "added":
        msg1 = f"✅ Clash 规则已添加\n[查看提交]({clash_url})"
    elif clash_status == "exists":
        msg1 = "⚠ Clash 规则中已存在"
    else:
        msg1 = "❌ Clash 规则添加失败"

    # Loon 添加逻辑
    loon_url, loon_status = g.add_rule_to_file(config['github']['loon_rule_path'], loon_rule, commit_message)
    if loon_status == "added":
        msg2 = f"✅ Loon 规则已添加\n[查看提交]({loon_url})"
    elif loon_status == "exists":
        msg2 = "⚠ Loon 规则中已存在"
    else:
        msg2 = "❌ Loon 规则添加失败"

    await update.message.reply_text(f"识别到域名：`{domain}`\n\n{msg1}\n{msg2}", parse_mode='Markdown')

def main():
    logging.basicConfig(level=logging.INFO)
    app = ApplicationBuilder().token(config['telegram_token']).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("query", query))
    app.add_handler(MessageHandler(filters.TEXT & (~filters.COMMAND), handle))
    app.run_polling()

if __name__ == "__main__":
    main()
