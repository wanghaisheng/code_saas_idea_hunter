
from top_github_scraper import get_top_repo_urls, get_top_repos, get_top_contributors, get_top_user_urls, get_top_users

if __name__=='__main__':
    keyword = "genshin"
    stop_page = 200
    get_top_repo_urls(keyword,sort_by='update',save_directory='data/'+keyword)
    # get_top_repos(keyword,sort_by='update',save_directory='data/'+keyword)
    # get_top_contributors(keyword, stop_page=stop_page)

    # get_top_users(keyword, stop_page=stop_page)