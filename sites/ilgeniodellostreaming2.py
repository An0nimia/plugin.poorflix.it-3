#!/usr/bin/python3

from hosts import hosts
from bs4 import BeautifulSoup
from requests import post, get
from hosts.exceptions.exceptions import VideoNotAvalaible

from scrapers.utils import (
	recognize_link, recognize_mirror,
	m_identify, get_domain, headers
)

try:
	from utils import new_way
except ImportError:
	from sites.utils import new_way

host = "https://ilgeniodellostreaming.cyou/"
excapes = ["Back", "back", ""]
timeout = 4
is_cloudflare = False

def search_film(film_to_search):
	search_data = {
		"story": film_to_search,
		"do": "search",
		"subaction": "search"
	}

	body = post(
		host,
		params = search_data,
		headers = headers,
		timeout = timeout
	).text

	parsing = BeautifulSoup(body, "html.parser")

	json = {
		"results": []
	}

	how = json['results']

	for a in parsing.find_all("div", class_ = "result-item"):
		image = a.find("img").get("src")
		some = a.find_all("a")[1]
		link = some.get("href")
		title = some.get_text()

		data = {
			"title": title,
			"link": link,
			"image": host + image
		}

		how.append(data)

	return json
	
def search_mirrors(film_to_see):
	domain = get_domain(film_to_see)
	body = get(film_to_see).text
	parsing = BeautifulSoup(body, "html.parser")
	options = parsing.find("ul", class_ = "options-list")

	try:
		json = new_way(film_to_see)
		return json
	except:
		pass

	json = {
		"results": []
	}

	datas = json['results']

	for a in options.find_all("li"):
		option = a.find("a")
		thing = option.get_text().split(" ")

		mirror = recognize_mirror(
			thing[0].replace("http:", "")
		)

		try:
			hosts[mirror]
			quality = thing[-1]

			link_mirror = recognize_link(
				option.get("data-link")
			)

			data = {
				"mirror": mirror,
				"quality": quality,
				"link": link_mirror,
				"domain": domain
			}

			datas.append(data)
		except KeyError:
			pass

	return json

def identify(info):
	link = info['link']
	mirror = info['mirror']
	domain = info['domain']
	link = m_identify(link)
	return hosts[mirror].get_video(link, domain)

def menu():
	while True:
		try:
			ans = input("Type the film title which you would search: ")
			result = search_film(ans)['results']

			while True:
				for a in range(
					len(result)
				):
					print(
						"%d): %s" % 
						(
							a + 1,
							result[a]['title']
						)
					)

				ans = input("What film do you want to see?: ")

				if ans in excapes:
					break

				index = int(ans) - 1
				film_to_see = result[index]['link']
				datas = search_mirrors(film_to_see)['results']

				while True:
					for a in range(
						len(datas)
					):
						print(
							"%s): %s (%s)"
							% (
								a + 1,
								datas[a]['mirror'],
								datas[a]['quality']
							)
						)

					ans = input("What film do you want to see?: ")

					if ans in excapes:
						break

					index = int(ans) - 1

					try:
						video = identify(datas[index])
					except VideoNotAvalaible as a:
						print(a)
						continue

					print(video)
		except KeyboardInterrupt:
			break

if __name__ == "__main__":
	menu()