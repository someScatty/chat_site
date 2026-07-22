import sys, re
from typing import TYPE_CHECKING, Any
from datetime import datetime
import traceback
class Colors:
    RESET = "\033[0m"
    RED = "\033[31m"
    YELLOW = "\033[33m"
    GREEN = "\033[32m"
    BLUE = "\033[34m"
    CYAN = "\033[36m"
    GRAY = "\033[90m"


if TYPE_CHECKING:
    from fyenid.app import ChatApp
class Logger:
    def __init__(self, parent: "ChatApp") -> None:
        self.stdout = sys.stdout
        self.stderr = sys.stderr
        self.parent = parent

    def _process_args(self, args: tuple[Any, ...], join: str = " ") -> str:
        msg: list[str] = []
        decimal_pattern = re.compile(r"(?<!\w)(\d+\.\d+)(?!\w)")
        product_name = getattr(getattr(self.parent, "config", None), "product_name", "")
        for obj in args:
            try:
                value = str(obj)
                #chatify
                value = value.replace(product_name, f"{Colors.BLUE}{product_name}{Colors.RESET}")
                value = decimal_pattern.sub(f"{Colors.CYAN}\\1{Colors.RESET}", value)
                msg.append(value)
            except Exception:
                pass
        return join.join(msg)
    
    def _timestamp(self) -> str:
        '''Generates a timestamp'''
        return datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    
    def _exception(self, exp: type[BaseException]) -> str:
        '''Generates a print statement for an exception'''
        return "".join(traceback.format_exception(exp))

    def error(self, *args: Any, seperator: str = " ", attach_exception: bool = False):
        contents = self._process_args(args, join=seperator)
        message = f"{Colors.RED}ERROR: {Colors.RESET}{contents}{"\n"}"

        if attach_exception:
            exc_type, exc_value, tb = sys.exc_info()
            if exc_type:
                message += self._exception(exc_type)
        self.stderr.write(message)
        self.stderr.flush()

    def warn(self, *args: Any, seperator: str = " "):
        contents = self._process_args(args, join=seperator)
        message = f"{Colors.YELLOW}WARNING: {Colors.RESET}{contents}{"\n"}"
        self.stderr.write(message)
        self.stderr.flush()

    def info(self, *args: Any, seperator: str = " "):
        contents = self._process_args(args, join=seperator)
        message = f"{Colors.GRAY}LOG: {Colors.RESET}{contents}{"\n"}"
        self.stdout.write(message)
        self.stdout.flush()

    def success(self, *args: Any, seperator: str = " "):
        contents = self._process_args(args, join=seperator)
        message = f"{Colors.GREEN}SUCCESS: {Colors.RESET}{contents}{"\n"}"
        self.stdout.write(message)
        self.stdout.flush()

    def debug(self, *args: Any, seperator: str = " "):
        if getattr(self.parent, "config", False):
            if self.parent.config.debug is False:
                return
        
        contents = self._process_args(args, join=seperator)
        message = f"{Colors.GRAY}DEBUG: {Colors.RESET}{contents}{"\n"}"
        self.stdout.write(message)
        self.stdout.flush()
    
    def bar(self):
        length = 80
        st = "-" * length

        self.stdout.write(st)
        self.stdout.flush()


    def newline(self, stderr: bool = False):
        if stderr:
            self.stderr.write("\n")
            self.stderr.flush()
        self.stdout.write("\n")
        self.stdout.flush()
