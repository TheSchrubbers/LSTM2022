__author__ = 'avzgui'

import requests
from bs4 import BeautifulSoup


############# GET N PUBLIC DECLARATION ON vie-publique.fr ####################

n = 100
step = 10

print("Search for " + str(n) +  " declarations\n")

for b in range(0, n, step):

    print("\nGet " + str(step) + " results from declation " + str(b) + " to declaration " + str(b + step - 1) + "\n" )

    r = requests.get('http://www.vie-publique.fr/rechercher/recherche.php?query=&dateDebut=&dateFin=&b=' + str(b) + '&skin=cdp&replies='+ str(step) +'&filter=&date=&typeDoc=f/vp_type_discours/declaration&skin=cdp&auteur=&filtreAuteurLibre=&source=&q=')

    if r.status_code == 200:
        soup = BeautifulSoup(r.text)

        results = soup.find_all('p', attrs={'class': 'titre'})

        for result in results:
       
            ######## SCRAP ARTICLE'S INFORMATIONS ###########
        
            link = result.a.get('href').split( )[0]
        
            print("Get : " + link)
            r = requests.get(link)

            if r.status_code == 200:
                print("status : " + str(r.status_code))
                soup = BeautifulSoup(r.text)
    
                # Get the article's title
                title = soup.find('div', attrs={'class': 'title_article'})
                print "Titre : ", 
                print(title.h2.text)

                if "d&#0233bat" not in title.h2.text.lower() and "point presse" not in title.h2.text.lower() and "point de presse" not in title.h2.text.lower() and "communiqu&#0233 de presse" not in title.h2.text.lower() and "conf&#0233rence de presse" not in title.h2.text.lower() and "interview" not in title.h2.text.lower() and "tribune" not in title.h2.text.lower(): # Don't looking for this crap (yeah, it's ugly...)

                    # Get the article's keywords
                    keywords = soup.find('meta', attrs={'name': 'keywords'}).get('content').split(',')
                    print "Keywords : ",
                    print(keywords)

                    # Parse article's html content to simple text
                    print("Parse content")
                    col1 = soup.find('div', attrs={'class': 'col1'})

                    ti = False
                    content = ""
                    for p in col1.find_all('p')[:-1]: # -1 to don't get sources        
                        p_text = ""
                        if not ti:
                            if "ti :" in p.text:
                                ti = True
                                p_text = p.text.replace('ti : ', '')
                        else:
                            p_text = p.text
                        if p_text != "":
                            content += p_text.lower()
    
                    # Replace contraction words
                    for contraction in ["n'", "qu'", "d'", "l'", "s'"]:
                        content = content.replace(contraction, contraction[:-1] + 'e ')
                    content = content.replace('du', 'de le') # special case

                    # To consider ponctuation as word
                    for ponctuation in [',', ';', '.', '!', '?', ':']:
                        content = content.replace(ponctuation, ' ' + ponctuation + ' ')


                    # Split content to words
                    words = content.split( )

                    if words: # if there is words

                        ####### WRITE ARTICLE'S INFORMATIONS TO JSON #######
                        print("Prepare writing")


                        article = "{\n\t\"article\": {\n"

                        # Article's title
                        article += "\t\t\"title\": \"" + title.text.replace('\n', '') + "\"\n"
   
                        # Article's kewords
                        article += "\t\t\"keywords\": ["
                        while keywords[len(keywords)-1] == "": # clean end of list
                            keywords.pop()
                        for keyword in keywords[:-1]:
                            if keyword != "":
                                article += "\"" + keyword + "\", "
                        article += "\"" + keywords.pop() + "\"],\n"

                        # Article's sentence
                        article += "\t\t\"sentences\": [\n\t\t\t{"
                        w_id = 0
                        for word in words[:-1]:
 
                            article += str(w_id) + ": \"" + word + "\""
                
                            if word == "." or word == "!" or word == "?": # New sentence
                                article += "},\n\t\t\t{"
                                w_id = 0
                            else:
                                article += ","
                                w_id += 1
                        article += str(w_id) + ": \"" + words.pop() + "\"}\n\t\t]\n"

                        # EOF
                        article += "\t}\n}"

                        #Write
                        art_no = link.replace('.html', '').split('/').pop()
                        print("Write to : downloads/" + art_no + ".json\n\n")

                        if not os.path.exists('downloads'):
                                os.makedirs('downloads')
                        file = open("downloads/" + art_no + ".json", "w")
                        file.write(article.encode('utf8'))
                        file.close()
                else:
                    print("##################################################################################################")
                    print("################################## DEBAT | POINT PRESSE ##########################################")
                    print("##################################################################################################\n\n")
