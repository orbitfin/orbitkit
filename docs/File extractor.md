
## 如何使用文件抽取器 FileDispatcher
#### 需要安装的依赖包
- boto3
- requests

#### 其他需要
- 配置好 aws-cli 及其默认参数

#### 参数传递格式
```python
{
    'published': None,
    'text': '',
    'store_path': '',
    'file_name': '',
    'file_type': '',
    'bucket': '',
    'status': 'pending',
    'reason': 'Pending to process.'
}
```
