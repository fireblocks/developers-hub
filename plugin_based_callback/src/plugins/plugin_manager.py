import importlib.util
from typing import List
from src.plugins.interface import PluginInterface
from src.exceptions import PluginLoadError, PluginError


class PluginManager:
    def __init__(self):
        self.plugins: List[PluginInterface] = []

    async def _load_plugin(self, plugin_name: str, plugin_path: str = "src/plugins"):
        try:
            # Convert from snake_case to PascalCase to get the plugin class name
            class_name = "".join(word.capitalize() for word in plugin_name.split("_"))
            # Dynamic import based on the path
            module_spec = importlib.util.spec_from_file_location(class_name, f"{plugin_path}/{plugin_name}.py")
            if module_spec is None:
                raise PluginLoadError(f"Failed to find plugin {plugin_name} at {plugin_path}")
            module = importlib.util.module_from_spec(module_spec)
            module_spec.loader.exec_module(module)
            plugin_class = getattr(module, class_name)
            # Instantiate a plugin object
            plugin_instance = plugin_class()
            await plugin_instance.init()
            self.plugins.append(plugin_instance)
        except (ImportError, AttributeError) as e:
            raise PluginLoadError(f"Failed to load plugin {plugin_name}: {e}")
        except PluginError as e:
            raise PluginLoadError(f"Error in plugin {plugin_name}, Error: \n{e}")
        except Exception as e:
            raise PluginLoadError(f"Unexpected error loading plugin {plugin_name}. \nError: {e}")

    async def load_plugins(self, plugin_specs: List[str]):
        for plugin_spec in plugin_specs:
            try:
                # Splitting the plugin specification into name and path
                plugin_name, plugin_path = plugin_spec.split(":", 1)
                await self._load_plugin(plugin_name, plugin_path)
            except ValueError:
                # Assume default path if not specified
                await self._load_plugin(plugin_spec)
            except PluginLoadError:
                raise

    def get_plugins(self) -> List[PluginInterface]:
        return self.plugins

    async def process_request(self, data: dict) -> bool:
        """Run the main method (entry point) for each plugin"""
        for plugin in self.plugins:
            res = await plugin.process_request(data)
            if not res:
                return False
        return True
