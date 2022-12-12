from aiogram import Dispatcher
from .admin_check import AdminCheck
from .manager_check import ManagerCheck


def setup(dp: Dispatcher):
    dp.filters_factory.bind(AdminCheck)
    dp.filters_factory.bind(ManagerCheck)
