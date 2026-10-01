from html.parser import HTMLParser
class DivCounter(HTMLParser):
    def __init__(self):
        super().__init__()
        self.divs = 0
        self.tab_contents = 0
    def handle_starttag(self, tag, attrs):
        if tag == 'div':
            self.divs += 1
            for k,v in attrs:
                if k == 'class' and 'tab-content' in v:
                    self.tab_contents += 1
                    print(f"Found tab-content. Div depth: {self.divs}")
    def handle_endtag(self, tag):
        if tag == 'div':
            self.divs -= 1
p = DivCounter()
with open('templates/admin_dashboard.html', 'r', encoding='utf-8') as f:
    p.feed(f.read())
print(f"Final div balance: {p.divs}")
