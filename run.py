import pytest,os
"""
生成allure报告的脚本
"""

if __name__ == '__main__':
    pytest.main([
        '-v',
        '--alluredir=./report/temp',
        '--clean-alluredir',
    ])
    os.system('allure generate ./report/temp -o ./report/html --clean') # 生成报告
    os.system('allure open ./report/html') # 打开报告