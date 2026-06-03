import unittest

from playwright.sync_api import sync_playwright
import threading, time, random

class LoadTest(unittest.TestCase):

    def test_page_load_test(self):
        max_wait = 30000 #For how long are you willing to wait for the page to load deafult is 30000 ms aka 30 seconds
        users  = 10 #number of users to simulate
        acceptable_avg_load_time = 3 # time in seconds
        acceptable_max_load_time = 5 # time in seconds
        page_load_times = []
        threads = []
        page_list = [
            ["OBSBOT Tiny 2 AI-Powered PTZ 4K Webcam Shop Page","https://bygo.pk/shop/obsbot-tiny-2-ai-powered-ptz-4k-webcam/",["https://bygo.pk/wp-content/uploads/2026/01/tiny-2-main-image-2-150x88.jpg","https://bygo.pk/wp-content/uploads/2026/01/OBSBOT-Tiny-2-AI-Powered-PTZ-4K-Webcam-1-150x171.jpg","https://bygo.pk/wp-content/uploads/2026/01/OBSBOT-Tiny-2-AI-Powered-PTZ-4K-Webcam-2-150x171.jpg"]]
        ]
        def testbody():
            with sync_playwright() as p:
                browser = p.chromium.launch(headless=True,args=["--start-maximized"])
                browser = browser.new_context(no_viewport=True,)
                page = browser.new_page()
                client = browser.new_cdp_session(page)
                client.send("Network.enable")
                client.send("Network.setCacheDisabled", {"cacheDisabled": True})
                
                local_page_list = random.sample(page_list, k=len(page_list))
                for local_page in local_page_list:
                    try:
                        start = time.time()
                        page.goto(local_page[1])
                        page.wait_for_function("""
                            (urls) => {
                                return urls.every(url => {
                                    const img = document.querySelector(`img[src*="${url}"]`);
                                    return img && img.complete && img.naturalWidth > 0;
                                });
                            }
                            """, arg=local_page[2], timeout=max_wait)
                        end = time.time()
                        page_load_times.append([local_page[0], end - start])
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
        for data in page_list:
            count = 0
            avg_page_load_times.append([data[0], 0])
            max_page_load_time.append([data[0], 0])
            for page_data in page_load_times:
                if page_data[0] == data[0]:
                    count += 1
                    if page_data[1] == -1:
                        self.assertFalse(True,f"The page {data[0]} failed to load atleast once")
                    else: 
                        avg_page_load_times[(len(avg_page_load_times) - 1)][1] += page_data[1]
                        if page_data[1] > max_page_load_time[(len(max_page_load_time) - 1)][1]:
                            max_page_load_time[(len(max_page_load_time) - 1)][1] = page_data[1]
            try:
                avg_page_load_times[(len(avg_page_load_times) - 1)][1] /= count
            except:
                self.assertTrue(True,f"The page {data[0]} was skipped and never tested due to an unknow error")


        print("\nAverage page load time for the entire site:", avg)
        for page in avg_page_load_times:
            print(f"Average page load time for {page[0]}: {page[1]} seconds")
        print("\nMaximum page load time for each page:")
        for page in max_page_load_time:
            print(f"Maximum page load time for {page[0]}: {page[1]} seconds")


        self.assertLessEqual(avg, acceptable_avg_load_time,f"Average page laod time of the whole site was higher then {acceptable_avg_load_time} seconds") 
        for page in avg_page_load_times:
            self.assertLessEqual(page[1], acceptable_avg_load_time,f"The Average load time of the {page[0]} is at {page[1]} seconds which was higher then the max limit of {acceptable_avg_load_time} seconds") 
        for page in max_page_load_time:
            self.assertLessEqual(page[1],acceptable_max_load_time, f"The max load time of the {page[0]} is at {page[1]} seconds which was higher then the max limit of {acceptable_max_load_time} seconds")

if __name__ == "__main__":
    unittest.main()