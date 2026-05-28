from . import start_handler, menu_handlers, file_handlers

def setup_handlers(dp):
    dp.include_router(start_handler.router)
    dp.include_router(menu_handlers.router)
    dp.include_router(file_handlers.router)