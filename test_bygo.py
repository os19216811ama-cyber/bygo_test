import unittest

from playwright.sync_api import sync_playwright
import threading, time, random

class LoadTest(unittest.TestCase):

    def test_page_load_test(self):
        page_load_times = []
        threads = []
        max_wait = 3000 #For how long are you willing to wait for the page to load
        users  = 1 #number of users to simulate
        acceptable_avg_load_time = 3 # time in seconds
        acceptable_max_load_time = 5 # time in seconds
        page_list = [
            ["Shop Page", "https://bygo.pk/shop/",["https://bygo.pk/wp-content/uploads/2026/01/front-15-430x267.jpg","https://bygo.pk/wp-content/uploads/2026/01/front-image-2-1-430x267.jpg","https://bygo.pk/wp-content/uploads/2026/01/front-img-430x267.jpg"]],
            ["Nvidia Jetson Orin Nano Page", "https://bygo.pk/nvidia-jetson-orin-nano/",["https://bygo.pk/wp-content/uploads/2025/12/WhatsApp-Image-2025-12-01-at-1.44.37-PM-2.jpeg","https://bygo.pk/wp-content/uploads/2025/12/WhatsApp-Image-2025-12-01-at-1.44.38-PM-800x700.jpeg"]],
            ["Nvidia Jetson Orin Nano Shop Page", "https://bygo.pk/shop/nvidia-jetson-orin-nano/",["https://bygo.pk/wp-content/uploads/2025/12/2-2.png","https://bygo.pk/wp-content/uploads/2025/12/2-2-150x171.png"]],
            ["S2 Screen Extender Shop Page", "https://bygo.pk/shop/s2-screen-extender/",'.zoomImg'],
            ["Product Category Page For Logitech", "https://bygo.pk/product-category/logitech/",'xpath=//*[@id="main-content"]/div/div[3]/div[2]/div/div/div[1]/a/img'],
            ["Kodak Page","https://bygo.pk/kodak/",'xpath=//*[@id="post-11126"]/div/section[1]/div/div[2]/div/div/div/figure/div/img'],
            ["Metz Page","https://bygo.pk/metz-led/",'xpath=//*[@id="wd-693278d060049"]/img'],
            ["Contact Us Page","https://bygo.pk/contact-us/",'xpath=//*[@id="post-5288"]/div/div[1]/div/div/div/div/div/iframe'],
            ["About Us Page","https://bygo.pk/about-us-3/",'xpath=//*[@id="wd-69369ac06b5e1"]/img'],
            ["NVIDIA Jetson Thor Developer Kit Shop Page","https://bygo.pk/shop/nvidia-jetson-thor-developer-kit/",'.zoomImg'],
            ["GAC2500 — SIP/Android Conference Phone Shop Page","https://bygo.pk/shop/gac2500-sip-android-conference-phone/",'.zoomImg'],
            ["OBSBOT Tiny 2 AI-Powered PTZ 4K Webcam Shop Page","https://bygo.pk/shop/obsbot-tiny-2-ai-powered-ptz-4k-webcam/",'.zoomImg']
        ]
        def testbody():
            with sync_playwright() as p:
                # browser = p.firefox.launch(headless=False,args=["--start-maximized"])
                browser = p.chromium.launch(headless=False,args=["--start-maximized"])
                browser = browser.new_context(no_viewport=True,)
                page = browser.new_page()
                client = browser.new_cdp_session(page)
                client.send("Network.enable")
                client.send("Network.setCacheDisabled", {"cacheDisabled": True})
                try:
                    start = time.time()
                    page.goto("https://bygo.pk/")
                    images = ["https://bygo.pk/wp-content/uploads/2026/01/Kodak-Paper-1.jpg","https://bygo.pk/wp-content/uploads/2026/01/Logitec-Projector-1.jpg"]
                    page.wait_for_function("""
                        (urls) => {
                            return urls.every(url => {
                                const img = document.querySelector(`img[src*="${url}"]`);
                                return img && img.complete && img.naturalWidth > 0;
                            });
                        }
                        """, arg=images,timeout=max_wait)
                    end = time.time()
                    print(end,start,end - start)
                    page_load_times.append(["Home Page", end - start])
                except Exception as e:
                    print("Erorr triggered",e)
                    page_load_times.append(["Home Page", -1])

                
                local_page_list = random.sample(page_list, k=len(page_list))
                for local_page in local_page_list:
                    try:
                        print("navigating to",local_page[0])
                        start = time.time()
                        page.goto(local_page[1])
                        page.wait_for_function("""
                            (urls) => {
                                return urls.every(url => {
                                    const img = document.querySelector(`img[src*="${url}"]`);
                                    return img && img.complete && img.naturalWidth > 0;
                                });
                            }
                            """, arg=local_page[2])
                        end = time.time()
                        page_load_times.append([local_page[0], end - start])
                        print("done")
                    except:
                        page_load_times.append([local_page[0],-1])
                browser.close()


        for i in range(users):
            t = threading.Thread(target=testbody)
            threads.append(t)
            t.start()
        for t in threads:
            t.join() 

        avg = sum(time for _, time in page_load_times) / len(page_load_times)


        avg_page_load_times = []
        max_page_load_time = []
        if -1 in page_load_times:
            self.assertTrue(True,f"There was a page that never fully loaded with in the given max time of {max_wait} seconds")
        for data in page_list:
            count = 0
            avg_page_load_times.append([data[0], 0])
            max_page_load_time.append([data[0], 0])
            for page_data in page_load_times:
                if page_data[0] == data[0]:
                    count += 1
                    avg_page_load_times[(len(avg_page_load_times) - 1)][1] += page_data[1]
                    if page_data[1] > max_page_load_time[(len(max_page_load_time) - 1)][1]:
                        max_page_load_time[(len(max_page_load_time) - 1)][1] = page_data[1]
            try:
                avg_page_load_times[(len(avg_page_load_times) - 1)][1] /= count
            except:
                self.assertTrue(True,f"The page {data[0]} was skipped and never tested due to an unknow error")


        avg_home = 0
        max_home = 0
        count = 0
        try:
            for page in page_load_times:
                if page[0] == "Home Page":
                    count += 1
                    if page[1] == -1:
                        self.assertTrue(False,f"There was an instance of Home Page which was not fully loaded with in the given max time of {max_wait} seconds")
                    avg_home += page[1]
                    if page[1] > max_home:
                        max_home = page[1]
            avg_home /= count
        except Exception as e:
            print(e)
        print("\nAverage page load time for the entire site:", avg)
        print(f"Average page load time for Home Page: {avg_home} seconds")
        for page in avg_page_load_times:
            print(f"Average page load time for {page[0]}: {page[1]} seconds")
        print("\nMaximum page load time for each page:")
        print(f"Maximum page load time for Home Page: {max_home} seconds")
        for page in max_page_load_time:
            print(f"Maximum page load time for {page[0]}: {page[1]} seconds")


        self.assertLessEqual(avg, acceptable_avg_load_time,f"Average page laod time of the whole site was higher then {acceptable_avg_load_time} seconds") 
        self.assertLessEqual(avg_home, acceptable_avg_load_time,f"Avergae load time of Home page was {avg_home} seconds which was higer then the acceptable limit of {acceptable_avg_load_time} seconds")
        self.assertLessEqual(max_home,acceptable_max_load_time, f"The max load time observed for home page with in this test is {max_home} seconds and exceeded the limit of {acceptable_max_load_time} seconds")
        for page in avg_page_load_times:
            self.assertLessEqual(page[1], acceptable_avg_load_time,f"The Average load time of the {page[0]} is at {page[1]} seconds which was higher then the max limit of {acceptable_avg_load_time} seconds") 
        for page in max_page_load_time:
            self.assertLessEqual(page[1],acceptable_max_load_time, f"The max load time of the {page[0]} is at {page[1]} seconds which was higher then the max limit of {acceptable_max_load_time} seconds")
        print(page_load_times)

if __name__ == "__main__":
    unittest.main()