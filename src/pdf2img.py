
import fitz  # PyMuPDF
import os
import argparse

def pdf_to_images(pdf_path, output_folder=None, zoom_x=2.0, zoom_y=2.0):
    # 如果没有提供 output_folder，则使用 PDF 文件名作为输出文件夹
    if output_folder is None:
        pdf_dir = os.path.dirname(pdf_path)  # 获取 PDF 文件所在的目录
        pdf_name = os.path.splitext(os.path.basename(pdf_path))[0]  # 获取 PDF 文件名（不带扩展名）
        output_folder = os.path.join(pdf_dir, pdf_name)  # 在 PDF 文件所在目录下创建输出文件夹

    # 确保输出目录存在
    os.makedirs(output_folder, exist_ok=True)

    # 打开PDF文件
    pdf_document = fitz.open(pdf_path)
    
    # 设置放大倍数，控制图像清晰度
    matrix = fitz.Matrix(zoom_x, zoom_y)

    # 遍历每一页
    for page_number in range(pdf_document.page_count):
        page = pdf_document.load_page(page_number)  # 加载当前页
        pix = page.get_pixmap(matrix=matrix)  # 获取页面的像素图像，应用放大倍数
        image_path = os.path.join(output_folder, f"page_{page_number + 1}.png")  # 定义输出图像路径
        
        # 保存为PNG格式
        pix.save(image_path)
        print(f"Page {page_number + 1} saved as {image_path}")
    
    # 关闭PDF文件
    pdf_document.close()

def main():
    # 使用 argparse 解析命令行参数
    parser = argparse.ArgumentParser(description="Convert PDF pages to high-quality images.")
    parser.add_argument("pdf_path", help="Path to the input PDF file.")
    parser.add_argument("--output_folder", help="Folder to save the output images. If not provided, uses PDF filename as the folder name.")
    parser.add_argument("--zoom_x", type=float, default=2.0, help="Zoom factor in x-direction for image quality.")
    parser.add_argument("--zoom_y", type=float, default=2.0, help="Zoom factor in y-direction for image quality.")

    # 获取命令行参数
    args = parser.parse_args()

    # 调用 pdf_to_images 函数
    pdf_to_images(args.pdf_path, args.output_folder, args.zoom_x, args.zoom_y)

if __name__ == "__main__":
    main()

