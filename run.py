import pytest
import os
import shutil
"""
生成allure报告的脚本
"""

if __name__ == '__main__':
    pytest.main([
        '-v',
        '--alluredir=./report/temp',
        '--clean-alluredir',
    ])
    shutil.copy('./environment.xml', './report/temp')
    os.system('allure generate ./report/temp -o ./report/html --clean')
    os.system('allure open ./report/html')