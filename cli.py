import cmd
import os
import subprocess
import json

class ScrapyCmd(cmd.Cmd):
    intro = 'Welcome to the Scrapy CLI. Type help or ? to list commands.\n'
    prompt = '(scrapy) '

    def do_add_url(self, arg):
        'Add a URL to the list for scraping: add_url http://example.com'
        urls = arg.strip().split()
        if urls:
            with open('my_scraper/urls.txt', 'a') as f:
                for url in urls:
                    f.write(url + '\n')
            print(f"URLs added: {', '.join(urls)}")
        else:
            print("Please provide at least one URL.")

    def do_list_urls(self, arg):
        'List all URLs in the list for scraping: list_urls'
        if os.path.exists('my_scraper/urls.txt'):
            with open('my_scraper/urls.txt', 'r') as f:
                urls = f.readlines()
            if urls:
                print("URLs for scraping:")
                for url in urls:
                    print(url.strip())
            else:
                print("No URLs found.")
        else:
            print("No URLs found.")

    def do_clear_urls(self, arg):
        'Clear all URLs from the list: clear_urls'
        if os.path.exists('my_scraper/urls.txt'):
            os.remove('my_scraper/urls.txt')
            print("All URLs cleared.")
        else:
            print("No URLs to clear.")

    def do_set_proxy(self, arg):
        'Set proxy for scraping: set_proxy http://proxyserver:port'
        proxy = arg.strip()
        if proxy:
            with open('my_scraper/proxy.txt', 'w') as f:
                f.write(proxy)
            print(f"Proxy set to: {proxy}")
        else:
            print("Please provide a proxy URL.")

    def do_clear_proxy(self, arg):
        'Clear the proxy setting: clear_proxy'
        if os.path.exists('my_scraper/proxy.txt'):
            os.remove('my_scraper/proxy.txt')
            print("Proxy cleared.")
        else:
            print("No proxy to clear.")

    def do_run_scraper(self, arg):
        'Run the scraper: run_scraper'
        if os.path.exists('my_scraper/urls.txt'):
            proxy = None
            if os.path.exists('my_scraper/proxy.txt'):
                with open('my_scraper/proxy.txt', 'r') as f:
                    proxy = f.read().strip()
            command = ['python', 'my_scraper/scraper.py']
            if proxy:
                command.append(proxy)
            subprocess.run(command)
        else:
            print("No URLs found. Add URLs before running the scraper.")

    def do_launch_gui(self, arg):
        'Launch the GUI: launch_gui'
        subprocess.run(['python', 'my_scraper/gui.py'])

    def do_exit(self, arg):
        'Exit the Scrapy CLI: exit'
        print('Thank you for using Scrapy CLI.')
        return True

if __name__ == '__main__':
    ScrapyCmd().cmdloop()
