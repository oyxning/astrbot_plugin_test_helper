import asyncio
from astrbot.api import AstrBotConfig, logger
from astrbot.api.event import AstrMessageEvent, filter
from astrbot.api.star import Context, Star, register

@register(
    "插件测试小助手",
    "LumineStory",
    "一个通过指令热更新其他插件的开发辅助工具。",
    "1.0.2", # 版本升级，标记最终修复
    "https://github.com/oyxning/astrbot_plugin_test_helper"
)
class PluginTestHelper(Star):
    def __init__(self, context: Context, config: AstrBotConfig):
        super().__init__(context)
        self.config = config

    @filter.command("测试仓库更新", alias={"update_test_repo"})
    @filter.permission_type(filter.PermissionType.ADMIN)
    async def update_plugin_from_repo(self, event: AstrMessageEvent):
        """
        从配置的GitHub仓库地址热更新插件。
        """
        target_repo_url = self.config.get("target_repo_url")
        proxy = self.config.get("proxy") or None

        if not target_repo_url or "your-name/your-plugin-repo" in target_repo_url:
            yield event.plain_result(
                "❌ **目标仓库未配置!**\n"
                "请先前往本插件的配置页面，填入你想要更新的插件的GitHub仓库地址。"
            )
            return

        yield event.plain_result(f"🚀 **收到更新指令!**\n正在从以下地址拉取更新:\n{target_repo_url}")

        try:
            # ！！！最终、正确的修复：使用带有下划线的 _star_manager
            plugin_manager = self.context._star_manager
            
            # 安全检查，确保我们找到了正确的方法
            if not hasattr(plugin_manager, 'install_plugin'):
                logger.error("插件测试小助手：在 self.context._star_manager 上找不到 install_plugin 方法。")
                yield event.plain_result("❌ **更新失败!**\n内部错误：无法访问插件安装服务。请检查AstroBot版本。")
                return

            # 调用内置的安装/更新方法
            await plugin_manager.install_plugin(repo_url=target_repo_url, proxy=proxy)
            
            logger.info(f"插件 {target_repo_url} 更新成功。")
            yield event.plain_result("✅ **插件更新成功！**\n目标插件已刷新为最新版本。")

        except AttributeError:
             logger.error("插件测试小助手：访问 self.context._star_manager 失败。这可能意味着AstroBot的核心API已发生变化。")
             yield event.plain_result("❌ **更新失败!**\n内部错误：无法找到插件管理器。")
        except Exception as e:
            logger.error(f"通过指令更新插件 {target_repo_url} 时发生错误: {e}", exc_info=True)
            yield event.plain_result(
                f"❌ **插件更新失败!**\n"
                f"错误信息: {e}\n"
                "请检查仓库地址是否正确，以及服务器网络是否能够访问GitHub。"
            )

    async def terminate(self):
        logger.info("插件测试小助手已终止。")