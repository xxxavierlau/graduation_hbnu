import scrapy, re, json
from ..items import Crawler51JobItem
from ..tools import send_to_wechat_work


class Spider51jobSpider(scrapy.Spider):
    # Meta data generated by scrapy command line.
    name = 'spider_51job'
    allowed_domains = ['51job.com']

    url = input('输入你要爬取的url, 注意清除parameter: ')
    current_page_num = 1
    start_urls = [url + str(current_page_num) + '.html?']

    def parse(self, response):
        body = response.body.decode("gbk")

        # ERROR LOG: 忽略了 __ 和 = 之间的空格, 导致正则表达式匹配不到结果,引起index out of range错误
        data_search_result = re.findall('window.__SEARCH_RESULT__ =(.+)}</script>', str(body))
        # IMPORTANT TIPS: re.findall()返回一个列表,但只有一个结果,观察可知在数据结构上缺少一个},故拼接一个组成JSON,方便后续提取数据
        data_json_demo = data_search_result[0] + "}"
        data = json.loads(data_json_demo)
        job_list = data["engine_search_result"]

        # 处理item的数据
        item = Crawler51JobItem()
        for result in data["engine_search_result"]:
            item["job_href"] = result["job_href"]
            item["job_name"] = result["job_name"]
            item["providesalary_text"] = result["providesalary_text"]
            item["company_name"] = result["company_name"]
            item["workarea_text"] = result["workarea_text"]
            item["companytype_text"] = result["companytype_text"]
            item["workyear"] = result["workyear"]
            item["issuedate"] = result["issuedate"]
            item["companysize_text"] = result["companysize_text"]
            item["companyind_text"] = result["companyind_text"]
            yield item

        # 搜索页迭代, 如果搜索结果的列表长度不为0, 则继续下一页
        if len(job_list) != 0:
            self.current_page_num += 1
            yield scrapy.Request(self.url + str(self.current_page_num) + ".html?", callback=self.parse)
        else:
            # 需要减去最后404的那一页
            total_page_num = self.current_page_num - 1
            send_to_wechat_work('爬虫运行结束, 共爬取%d页。' % total_page_num)