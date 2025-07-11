# Imports all the tools in the tools directory
import pkgutil
__path__ = pkgutil.extend_path(__path__, __name__)
for importer, modname, ispkg in pkgutil.walk_packages(path=__path__, prefix=__name__ + '.'):
    if not ispkg: # Only import modules, not subpackages
        try:
            __import__(modname)
        except Exception as e:
            print(f"Could not import module {modname}: {e}")

from tools.tool_registry import TOOL_REGISTRY
__all__ = ['TOOL_REGISTRY'] # Expose only the TOOL_REGISTRY
