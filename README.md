# 批量翻译CSV文件

python脚本，通过调用智谱免费AI模型（glm-4-flash或者glm-4v-flash）来翻译CSV文件。程序通过读取input文件夹中的csv文件，将翻译结果保存到output文件夹中。

## 步骤

1. 【获取API KEY】 可以通过以下链接获取你的API keys： https://www.bigmodel.cn/usercenter/proj-mgmt/apikeys

2. 【修改配置信息】 修改代码中的CONFIG，将API_KEY修改为你的API KEY。你也可以修改input_folder，output_folder对应你的文件夹等。

3. 【运行代码】运行python translate_csv.py，程序会自动读取 input_folder 文件夹中的csv文件，将翻译结果保存到 output_folder 文件夹中。
