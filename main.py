import asyncio
from astrbot.api import AstrBotConfig, logger
from astrbot.api.event import AstrMessageEvent, filter
from astrbot.api.star import Context, Star, register

@register(
    "插件测试小助手",
    "LumineStory",
    "一个通过指令热更新其他插件的开发辅助工具。",
    "1.0.1", # 版本升级，标记修复
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
            # ！！！核心修复：获取插件管理器的正确方式
            # StarManager 是实际负责插件安装和管理的核心服务
            plugin_manager = self.context.star_manager
            
            # 检查获取到的对象是否正确
            if not hasattr(plugin_manager, 'install_plugin'):
                logger.error("意图路由器：无法在 self.context.star_manager 上找到 install_plugin 方法。")
                yield event.plain_result("❌ **更新失败!**\n内部错误：无法访问插件安装服务。")
                return

            # 调用内置的安装/更新方法
            await plugin_manager.install_plugin(repo_url=target_repo_url, proxy=proxy)
            
            logger.info(f"插件 {target_repo_url} 更新成功。")
            yield event.plain_result("✅ **插件更新成功！**\n目标插件已刷新为最新版本。")

        except Exception as e:
            logger.error(f"通过指令更新插件 {target_repo_url} 时发生错误: {e}", exc_info=True)
            yield event.plain_result(
                f"❌ **插件更新失败!**\n"
                f"错误信息: {e}\n"
                "请检查仓库地址是否正确，以及服务器网络是否能够访问GitHub。"
            )

    async def terminate(self):
        logger.info("插件测试小助手已终止。")