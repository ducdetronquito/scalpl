from copy import deepcopy
import json
from timeit import timeit
import unittest

from scalpl import Cut

from addict import Dict
from box import Box
import requests


class TestDictPerformance(unittest.TestCase):
    """
        Base class to test performance of different
        dict wrapper regarding insertion and lookup.
    """

    # We use a portion of the JSON dump of the Python Reddit page.

    PYTHON_REDDIT = {
        "kind": "Listing",
        "data": {
            "modhash": "",
            "dist": 27,
            "children": [
                {
                    "kind": "t3",
                    "data": {
                        "approved_at_utc": None, "subreddit": "Python",
                        "selftext": "Top Level comments must be **Job Opportunities.**\n\nPlease include **Location** or any other **Requirements** in your comment. If you require people to work on site in San Francisco, *you must note that in your post.* If you require an Engineering degree, *you must note that in your post*.\n\nPlease include as much information as possible.\n\nIf you are looking for jobs, send a PM to the poster.",
                        "author_fullname": "t2_628u", "saved": False,
                        "mod_reason_title": None, "gilded": 0, "clicked": False, "title": "r/Python Job Board", "link_flair_richtext": [],
                        "subreddit_name_prefixed": "r/Python", "hidden": False, "pwls": 6, "link_flair_css_class": None, "downs": 0, "hide_score": False, "name": "t3_cmq4jj",
                        "quarantine": False, "link_flair_text_color": "dark", "author_flair_background_color": "", "subreddit_type": "public", "ups": 11, "total_awards_received": 0,
                        "media_embed": {}, "author_flair_template_id": None, "is_original_content": False, "user_reports": [], "secure_media": None,
                        "is_reddit_media_domain": False, "is_meta": False, "category": None, "secure_media_embed": {}, "link_flair_text": None, "can_mod_post": False,
                        "score": 11, "approved_by": None, "thumbnail": "", "edited": False, "author_flair_css_class": "", "author_flair_richtext": [], "gildings": {},
                        "content_categories": None, "is_self": True, "mod_note": None, "created": 1565124336.0, "link_flair_type": "text", "wls": 6, "banned_by": None,
                        "author_flair_type": "text", "domain": "self.Python",
                        "allow_live_comments": False,
                        "selftext_html": "&lt;!-- SC_OFF --&gt;&lt;div class=\"md\"&gt;&lt;p&gt;Top Level comments must be &lt;strong&gt;Job Opportunities.&lt;/strong&gt;&lt;/p&gt;\n\n&lt;p&gt;Please include &lt;strong&gt;Location&lt;/strong&gt; or any other &lt;strong&gt;Requirements&lt;/strong&gt; in your comment. If you require people to work on site in San Francisco, &lt;em&gt;you must note that in your post.&lt;/em&gt; If you require an Engineering degree, &lt;em&gt;you must note that in your post&lt;/em&gt;.&lt;/p&gt;\n\n&lt;p&gt;Please include as much information as possible.&lt;/p&gt;\n\n&lt;p&gt;If you are looking for jobs, send a PM to the poster.&lt;/p&gt;\n&lt;/div&gt;&lt;!-- SC_ON --&gt;",
                        "likes": None, "suggested_sort": None, "banned_at_utc": None, "view_count": None, "archived": False, "no_follow": False, "is_crosspostable": False, "pinned": False,
                        "over_18": False, "all_awardings": [], "media_only": False, "can_gild": False, "spoiler": False, "locked": False, "author_flair_text": "reticulated",
                        "visited": False, "num_reports": None, "distinguished": None, "subreddit_id": "t5_2qh0y", "mod_reason_by": None, "removal_reason": None, "link_flair_background_color": "",
                        "id": "cmq4jj", "is_robot_indexable": True, "report_reasons": None, "author": "aphoenix", "num_crossposts": 0, "num_comments": 2, "send_replies": False, "whitelist_status": "all_ads",
                        "contest_mode": False, "mod_reports": [], "author_patreon_flair": False, "author_flair_text_color": "dark",
                        "permalink": "/r/Python/comments/cmq4jj/rpython_job_board/", "parent_whitelist_status": "all_ads", "stickied": True,
                        "url": "https://www.reddit.com/r/Python/comments/cmq4jj/rpython_job_board/", "subreddit_subscribers": 399170, "created_utc": 1565095536.0,
                        "discussion_type": None, "media": None, "is_video": False
                    }
                }
            ]
        }
    }

    namespace = {
        'Wrapper': dict
    }

    def setUp(self):
        self.data = deepcopy(self.PYTHON_REDDIT)
        self.namespace.update(self=self)

    def execute(self, statement, method):
        n = 1000
        time = timeit(statement, globals=self.namespace, number=n)
        print(
            '# ',
            self.namespace['Wrapper'],
            ' - ',
            method,
            ': ',
            int(60 / (time/n)),
            ' ops per second.'
        )

    def test_init(self):
        self.execute('Wrapper(self.data)', 'instanciate')

    def test_getitem(self):
        self.execute("Wrapper(self.data)['data']['modhash']", 'get')

    def test_getitem_through_list(self):
        statement = (
            "Wrapper(self.data)['data']['children'][0]['data']['author']"
        )
        self.execute(statement, 'get through list')

    def test_setitem(self):
        statement = "Wrapper(self.data)['data']['modhash'] = 'dunno'"
        self.execute(statement, 'set')

    def test_setitem_through_list(self):
        statement = (
            "Wrapper(self.data)['data']['children'][0]"
            "['data']['author'] = 'Captain Obvious'"
        )
        self.execute(statement, 'set through list')


class TestCutPerformance(TestDictPerformance):

    namespace = {
        'Wrapper': Cut
    }

    def test_getitem(self):
        self.execute("Wrapper(self.data)['data.modhash']", 'get')

    def test_getitem_through_list(self):
        statement = (
            "Wrapper(self.data)['data.children[0].data.author']"
        )
        self.execute(statement, 'get through list')

    def test_setitem(self):
        statement = "Wrapper(self.data)['data.modhash'] = 'dunno'"
        self.execute(statement, 'set')

    def test_setitem_through_list(self):
        statement = (
            "Wrapper(self.data)['data.children[0]"
            ".data.author'] = 'Captain Obvious'"
        )
        self.execute(statement, 'set through list')


class TestBoxPerformance(TestDictPerformance):

    namespace = {
        'Wrapper': Box
    }

    def test_getitem(self):
        self.execute("Wrapper(self.data).data.modhash", 'get - 1st lookup')
        self.execute("Wrapper(self.data).data.modhash", 'get - 2nd lookup')

    def test_getitem_through_list(self):
        statement = (
            "Wrapper(self.data).data.children[0].data.author"
        )
        self.execute(statement, 'get through list - 1st lookup')
        self.execute(statement, 'get through list - 2nd lookup')

    def test_setitem(self):
        statement = "Wrapper(self.data).data.modhash = 'dunno'"
        self.execute(statement, 'set - 1st lookup')
        self.execute(statement, 'set - 2nd lookup')

    def test_setitem_through_list(self):
        statement = (
            "Wrapper(self.data).data.children[0]"
            ".data.author = 'Captain Obvious'"
        )
        self.execute(statement, 'set through list - 1st lookup')
        self.execute(statement, 'set through list - 2nd lookup')


class TestAddictPerformance(TestDictPerformance):

    namespace = {
        'Wrapper': Dict
    }


if __name__ == '__main__':
    unittest.main()
