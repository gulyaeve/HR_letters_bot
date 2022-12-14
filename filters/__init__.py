from aiogram import Dispatcher
from .authcheck import AuthCheck
from .admin_check import AdminCheck
from .manager_check import ManagerCheck


def setup(dp: Dispatcher):
    dp.filters_factory.bind(AuthCheck)
    dp.filters_factory.bind(AdminCheck)
    dp.filters_factory.bind(ManagerCheck)
