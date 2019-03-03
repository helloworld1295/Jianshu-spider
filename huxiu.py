
from selenium import webdriver
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
import re
from urllib.request import urlopen
from PIL import Image
from selenium.webdriver import ActionChains
import time


class Crack():
    def __init__(self):
        self.url = "https://www.huxiu.com/"
        self.driver = webdriver.Chrome()
        self.wait = WebDriverWait(self.driver,20)
        self.driver.set_window_size(1920,1080
            )
        self.driver.get(self.url)
    
    def signup(self):  
        self.driver.get(self.url)
        buttonTag = self.wait.until(EC.element_to_be_clickable((By.CLASS_NAME,'js-register')))
        buttonTag.click()
        gt_cut_bg = "//div[@class='gt_cut_bg gt_show']/div"
        image_file_name_0 = 'cut_bg.jpg'
        cut_bg = self.get_img(gt_cut_bg, image_file_name_0)

        
        get_cut_fullbg_slice = "//div[@class='gt_cut_fullbg gt_show']/div"
        img_file_name_1 = 'cut_fullbg_slice.jpg'
        cut_fullbg_slice = self.get_img(get_cut_fullbg_slice, img_file_name_1)
        

        #计算缺口位置的x坐标
        loc_x = self.get_gap(cut_bg,cut_fullbg_slice)
        print('移动至：',loc_x)

        self.move_to_gap(loc_x)


    #找到图片    
    def get_img(self,img_xpath,img_file_name):
        image_divs = self.wait.until(EC.presence_of_all_elements_located((By.XPATH, img_xpath)))
        imageurl = re.findall(r'background-image: url\("(.*)"\);', image_divs[0].get_attribute("style"))[0].replace("webp", "jpg")
        print(imageurl)
        with open(img_file_name,'wb') as f:
            img = urlopen(imageurl).read()
            f.write(img)

        location_list = []
        for image in image_divs:
            location = {}
            loc_find = re.findall(r"background-position: (.*?)px (.*?)px;", image.get_attribute("style"))
            location['x'] = int(loc_find[0][0])
            location['y'] = int(loc_find[0][1])
            location_list.append(location)
        print(location_list)
        image_new = self.get_merge_image(img_file_name, location_list)
        return image_new
    

    def get_merge_image(self,img_file_name,location_list):
        im = Image.open(img_file_name)
        im_list_upper = []
        im_list_down = []

        #根据52个div的x和y坐标，进行循环，把打乱的图切割成52个小图片
        for location in location_list:
            if location['y'] == -58:
                #宽度==10
                #print(abs(location['x']),58,abs(location['x']) + 10 ,116)
                im_list_upper.append(im.crop((abs(location['x']),58,abs(location['x']) + 10,116)))
            elif location['y'] == 0:
                im_list_down.append(im.crop((abs(location['x']), 0, abs(location['x']) + 10, 58)))

        #建立一个新图片
        new_im = Image.new('RGB',(260,116))
        x_offset = 0
        #根据下图片列表，把小图片按照 x和y坐标，粘贴到 new_im
        for im in im_list_upper:
            new_im.paste(im,(x_offset,0))
            x_offset += im.size[0]
            
        x_offset = 0
        # 根据下图片列表，把小图片按照 x和y坐标，粘贴到 new_im
        for im in im_list_down:
            new_im.paste(im, (x_offset, 58))
            x_offset += im.size[0]

        new_im.save(img_file_name.replace(".jpg", "_merge.jpg"))
        return new_im


    #判断两个像素是否相同
    def is_pixel_equal(self, image1, image2, x, y):
        #取两个图片的像素点
        threshold = 55
        pixel1 = image1.getpixel((x, y))
        pixel2 = image2.getpixel((x, y))
        # print(pixel1)
        # print(pixel2)

        for i in range(0,3):
             if abs(pixel1[i] - pixel2[i]) >= threshold:
                 return False
        return True

    def get_gap(self,image1,image2):
        '''
        获取缺口的起始位置
        ：param image1:不带缺口的图片
        ：param image2 带缺口的图片
        '''
        x = 0
        for x in range(0,260):
            for y in range(0,116):
                if not self.is_pixel_equal(image1,image2,x,y):
                #返回第一像素不同的位置 x的坐标 即 滑块开始的地方至缺口x位置
                    return x


    def get_track(self,distance):
        '''
        根据偏移量获取对应轨迹
        先做做匀速运动 后匀减速运动
        ：param distance
        return 移动轨迹
        '''

        #滑块起始位置与图片边缘有点点的差距 可做点调整
        distance -= 2.4
        track = []
        current = 0
        mid = distance * 4 /5
        t = 0.2
        v =0
        while current < distance:
            if current < mid:
                a = 0.8
            else:
                a = -3
                
            v0 = v
            v = v0 +a * t
            move = v0*t +1/2 * a * t * t
            current += move
            track.append(round(move))
        return track

    def move_to_gap(self,distance):
        '''
        拖动至滑块缺口处
        '''
        tracks = self.get_track(distance)
        #滑块
        slider_button = self.wait.until(EC.element_to_be_clickable((By.XPATH,"//div[@class='gt_slider_knob gt_show']")))

        #移动
        ActionChains(self.driver).click_and_hold(slider_button).perform()
        for x in tracks:
            ActionChains(self.driver).move_by_offset(xoffset=x, yoffset=0).perform()
        time.sleep(0.5)
        ActionChains(self.driver).release().perform()
        time.sleep(6)
        self.signup()
        
        
    def run(self):
        self.signup()


if __name__ == "__main__":
    crack = Crack()
    crack.run()

        
        

        
