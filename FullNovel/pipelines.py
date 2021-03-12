# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://docs.scrapy.org/en/latest/topics/item-pipeline.html


# useful for handling different item types with a single interface
from itemadapter import ItemAdapter
import os


class FullnovelPipeline:
    def process_item(self, item, spider):
        # dir_name = str(item['b_category'])
        dir_path = './hongxiu/'
        if not os.path.exists(dir_path):
            os.mkdir(dir_path)
        file_path = dir_path+'total_category'+'.csv'
        with open(file_path, 'ab') as f:
            f.write((str(item['b_name'])+','+str(item['b_author'])+','+str(item['b_type'])+','+str(item['b_intro'])+','
                     +str(item['b_click'])+'\n').encode('utf-8'))
        return item
