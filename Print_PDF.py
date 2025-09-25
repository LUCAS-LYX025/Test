# -*- coding: utf-8 -*-

"""
@author: lucas
@Function:
@file: Print_PDF.py
@time: 2023/12/12 17:10
"""
import PyPDF2


def extract_text_from_pdf(file_path, start_page=None, end_page=None):
    with open(file_path, 'rb') as file:
        reader = PyPDF2.PdfReader(file)
        num_pages = len(reader.pages)

        # 设置起始页和结束页，默认为整个文档
        if start_page is None:
            start_page = 0
        if end_page is None or end_page > num_pages:
            end_page = num_pages

        text = ""
        for page_number in range(start_page, end_page):
            page = reader.pages[page_number]
            text += page.extract_text()
        print(text)
        return text


def print_pdf_to_txt(file_path, txt_file_path, start_page=None, end_page=None):
    # 从 PDF 中提取文本内容
    text = extract_text_from_pdf(file_path, start_page, end_page)

    # 将文本内容写入 TXT 文件中
    with open(txt_file_path, 'w') as txt_file:
        txt_file.write(text)


# 调用函数并传入PDF文件路径、TXT文件路径和章节范围
print_pdf_to_txt('/Users/leiyuxing/pt/Python.pdf', '/Users/leiyuxing/pt/trans.txt', start_page=1, end_page=15)


#
# def extract_text_from_pdf(file_path, start_page=None, end_page=None):
#     with open(file_path, 'rb') as file:
#         reader = PyPDF2.PdfReader(file)
#         num_pages = len(reader.pages)
#
#         # 设置起始页和结束页，默认为整个文档
#         if start_page is None:
#             start_page = 0
#         if end_page is None or end_page > num_pages:
#             end_page = num_pages
#
#         text = ""
#         for page_number in range(start_page, end_page):
#             page = reader.pages[page_number]
#             extracted_text = page.extract_text()
#
#             # 去除样式
#             # cleaned_text = re.sub(r'\n+', '\n', extracted_text)
#             cleaned_text = re.sub(r'\s+', ' ', extracted_text)
#
#             text += cleaned_text
#
#         return text
# #
# #
# # def print_pdf_to_txt(file_path, txt_file_path, start_page=None, end_page=None):
# #     # 从 PDF 中提取文本内容
# #     text = extract_text_from_pdf(file_path, start_page, end_page)
# #
# #     # 将文本内容写入 TXT 文件中
# #     with open(txt_file_path, 'w') as txt_file:
# #         txt_file.write(text)
# #
# #
# # # 调用函数并传入PDF文件路径、TXT文件路径和章节范围
# # print_pdf_to_txt('/Users/leiyuxing/pt/Python.pdf', '/Users/leiyuxing/pt/transform.txt', start_page=317, end_page=344)
# import PyPDF2
# import re
#
#
# def print_pdf_to_plain_text(file_path, plain_text_file_path, start_page=None, end_page=None):
#     # 从 PDF 中提取文本内容
#     text = extract_text_from_pdf(file_path, start_page, end_page)
#
#     # 去除样式但保留换行符
#     cleaned_text = re.sub(r'<.*?>', '', text)
#     cleaned_text = re.sub(r'\n+', '\n', cleaned_text)
#
#     # 将纯文本内容写入文件中
#     with open(plain_text_file_path, 'w') as text_file:
#         text_file.write(cleaned_text)
#
# # 调用函数并传入PDF文件路径、纯文本文件路径和章节范围
# print_pdf_to_plain_text('/Users/leiyuxing/pt/Python.pdf', '/Users/leiyuxing/pt/transform.txt', start_page=317, end_page=344)