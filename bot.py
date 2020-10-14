# bot.py
#mainguild ajouté -> voir pour l'utiliser
#corriger bug avec prof
#ajouter afficher agenda tout les matins.
import os
import discord
from dotenv import load_dotenv
import mysql.connector
from datetime import datetime
from datetime import date

GUILDID = 689815391026937895

DATABASE = "botenda"

KEYWORD = "/dev"
FILENAME = "/home/pi/workspace/Botenda/releases/Alpha/log.log"
PROF = 690558270141890590
DELEG = 690558330778943558
MODO = 690558366128275517
AGEND = 691949967496970281
#ALPHABET = ['a', 'b', 'c', 'd', 'e', 'f', 'g', 'h', 'i', 'j', 'k', 'l', 'm', 'n', 'o', 'p', 'q', 'r', 's', 't', 'u', 'v', 'w', 'x', 'y', 'z']

#GUILDFILE = "guild.pobj"

load_dotenv()
TOKEN = os.getenv('DISCORD_TOKEN')

DE = ["start", " h1 "]
A = ["end", " h2 "]
LE = ["event_date", " dte "]
POUR = ["concern", " pour "]

class TimeError(Exception):
	def __init__(self, h, m):
		self.h = h
		self.m = m
	def getErrorFrom(self):
		rtn = dict()
		if self.h<0 or self.h>23:
			rtn['h'] = self.h
		if self.m<0 or self.m>59:
			rtn['m'] = self.m
		return rtn

def sortSecond(val):
	return val[1]

def isUserID(string):
	if len(string)==18:
		for c in string:
			if (c=='0' or c=='1' or c=='2' or c=='3' or c=='4' or c=='5' or c=='6' or c=='7' or c=='8' or c=='9')==False:
				return False
		return True
	else:
		return False
def startWord(string, keyword):
	if len(string)==len(keyword):
		return string == keyword
	elif len(string)>len(keyword):
		return string[:len(keyword)+1] == (keyword + " ")
	else:
		return False

def makeTime(tm):
	bufh1 = tm.split("h")
	m1="00"
	if bufh1[1]!="":
		m1 = (bufh1[1])
	if int(m1)<0 or int(m1)>59:
		raise TimeError(int(bufh1[0]), int(m1))
	return bufh1[0] + ":" + m1 + ":00"

class Botenda(discord.Client):
	"""Child class of CLient"""
	async def on_ready(self):
		print("Logged on as " + str(self.user))
		self.cnx = mysql.connector.connection.MySQLConnection()
		self.logFile = open(FILENAME, "a")
		self.logFile.close()
		self.writeLog("Botenda started\n")
		self.mainGuildSET = False

	async def on_guild_join(self, guild):
		self.guild = guild
		print("JOIN A GUILD: " + str(guild.name))
		self.writeLog("Join a guild, the guild's name is " + str(guild.name) + "\n")
		print(guild.members)
		for member in guild.members:
			print(member)
			try:
				role = self.getRolesUser(member, guild)
				dmchan = await member.create_dm()
				await dmchan.send(self.getHelp(member, guild, True))
				self.writeLog("Send help in DM to : " + str(member.name))
			except:
				pass
			#FINIR send help to every users !
		#self.guild = guild
		#print("JOIN A GUILD : " + str(self.guild.name))
		#with open(GUILDFILE, 'wb') as file:
		#	pickr = pickle.Pickler(file)
		#	pickr.dump(self.guild)

	async def on_message(self, message):
		if self.mainGuildSET==False and message.guild.id==GUILDID:
			self.mainGuild = message.guild
			self.mainGuildSET = True
		try:
			self.xxx = open("." + str(message.guild) + "." + str(message.channel) + ".log", "a")
			self.xxx.write(str(datetime.now()) + "|" + str(message.id) + "::" + str(message.author) + "@" + str(message.author.nick) + ": " + str(message.content) + '\n')
			self.xxx.close()
		except AttributeError:
			self.xxx = open("." + str(message.guild) + "." + str(message.channel) + ".log", "a")
			self.xxx.write(str(datetime.now()) + "|" + str(message.id) + "::" + str(message.author) + "@None" + ": " + str(message.content) + '\n')
			self.xxx.close()
		if message.author != self.user:
			#print(message.content)
			#role = discord.utils.get(message.guild.roles, name="TSSI2")
			#print(role.id)
			#print(role.members)
			#print(self.takeBtween(message.content, " de ", " a "))
			if startWord(message.content, KEYWORD):
				#async with message.channel.typing():
				await message.channel.trigger_typing()
				self.lastChan = message.channel
				print("call")
				bufWords = message.content.split(" ")
				#print(bufWords)
				words = []
				for i in bufWords:
					if i != "":
						words.append(i)
				print(words)
				try:
					if len(words)==1:	#-----------------------Agenda Perso----------------------------------------------------------------------------------------------------
						roles = self.getRolesUser(message.author, message.guild)
						#print(roles)
						namesRoles = []
						for role in roles:
							namesRoles.append(role.name)
							namesRoles.append("<@&" + str(role.id) + ">")
						namesRoles.append(message.author.name)
						#print(self.getNickname(message.author, message.guild))
						dte = str(date.today())
						print(dte)
						rows = self.selectEntry(len(namesRoles), namesRoles, dte, False, "<@!" + str(message.author.id) + ">")
						if len(rows)>0:
							await message.channel.send("Agenda de <@!" + str(message.author.id) + ">" + ":\n" + self.getAgenda(rows))#, self.getNickname(message.author, message.guild)))
						else:
							await message.channel.send("<@!" + str(message.author.id) + ">, votre agenda est vide. :relieved:")
					elif words[1]=="add":	#------------------------------ADD-----------------------------------------------------------------------------------------------------------------
						#print(self.getRolesUser(message.author, message.guild))
						roles = self.getRolesUser(message.author, message.guild)
						if self.hasRole(roles, PROF) or self.hasRole(roles, MODO) or self.hasRole(roles, DELEG) or self.hasRole(roles, AGEND):
							if len(words)<9:
								await message.channel.send("Erreur de syntaxe")
								await message.channel.send("Syntaxe correcte:\n**/agenda add** Matière **de** Heure début **à** Heure fin **le** date **pour** Rôle")
							else:
								#await message.channel.send("Ajouter dans l'agenda")
								buf = message.content[9:]
								checkR = True
								checkLambda = True
								while buf[0] == " ":
									buf = buf[1:]
								if buf.find(" à ")!=-1:
									sep = " à "
								else:
									sep = " a "
								rows = []
								rows.append(buf.split(" de ")[0])
								print(rows[0])
								rows.append("")
								rows.append((buf.split(" de ")[1]).split(sep)[0])
								rows.append(((buf.split(" de ")[1]).split(sep)[1]).split(" le ")[0])
								dte = (((buf.split(" de ")[1]).split(sep)[1]).split(" le ")[1]).split(" pour ")[0]
								if buf.find(" avec ") == (-1):
									if self.hasRole(roles, PROF)==False:#self.hasRole(roles, MODO) or self.hasRole(roles, DELEG):
										await message.channel.send("Tu n'est pas professeur. Tu doit définir un professeur pour ce cour avec\n**/agenda add** Cour **de** HeureDebut **à** HeureFin **le** Date **pour** GroupeEleve **avec** Professeur")
										checkR = False
									else:
										rows.append((((buf.split(" de ")[1]).split(sep)[1]).split(" le ")[1]).split(" pour ")[1])
										rows.append("<@!" + str(message.author.id) + ">")
								else:
									rows.append((((buf.split(" de ")[1]).split(sep)[1]).split(" le ")[1]).split(" pour ")[1].split(" avec ")[0])
									prof = (((buf.split(" de ")[1]).split(sep)[1]).split(" le ")[1]).split(" pour ")[1].split(" avec ")[1]
									if prof.find("<@!")==-1:
										await message.channel.send("Tu dois nommer le prof avec un @.\nSi le professeur n'existe pas, ça ne peut pas fonctionner.  :expressionless:.\n")
										checkLambda = False
									else:
										rows.append(prof)

								checkT = True
								checkTa= True
								timeErrorFrom = dict()
								if checkLambda:
									bufDate = dte.split("/")
									dte = str(datetime.now().year) + "-" + bufDate[1] + "-" + bufDate[0]
									rows[1] = dte

									checkT = True
									timeErrorFrom = dict()
									try:
										rows[2] = makeTime(rows[2])
										rows[3] = makeTime(rows[3])
									except TimeError as e:
										checkT = False
										timeErrorFrom = e.getErrorFrom()
									#for i in range(h1, h2+1):
									#	h.append(i)
									#for i in range(m1, m2+1):
									#	m.append(i)

									print(rows)
									param = dict()
									param['concern'] = rows[4]
									param['start'] = rows[2]
									param['end'] = rows[3]
									param['event_date'] = rows[1]
									param['owner'] = rows[5]

									taken = self.selectEntryPlus(param)
									if len(taken)>0:
										checkTa = False
									else:
										checkTa = True

								if checkR and checkT and checkTa and checkLambda:
									self.addEntry(rows)
									buf1 = rows[1].split("-")
									await message.channel.send(rows[4] + " aura " + rows[0] + " le " + buf1[2] + "/" + buf1[1] + "/" + buf1[0] + " de " + rows[2][:-3] + " à " + rows[3][:-3] + " avec " + rows[5])
									self.writeLog(str(message.author) + "@" + str(message.author.nick) + " from " + str(message.channel) + ": " + str(message.content) + "\n")
								elif checkT==False:
									await message.channel.send("Erreur dans la définition des heures de cours.")
									if 'h' in timeErrorFrom:
										await message.channel.send("Les heures doivent être comprises entre 0 et 23. Vous avez défini l'heure à : " + str(timeErrorFrom['h']))
									if 'm' in timeErrorFrom:
										await message.channel.send("Les minutes doivent être comprises entre 0 et 59. Vous avez défini les minutes à : " + str(timeErrorFrom['m']))
									self.writeLog(str(message.author) + "@" + str(message.author.nick) + " from " + str(message.channel) + ": " + str(message.content) + " -> ECHEC TIMEDEF\n")
								elif checkTa==False:
									if self.hasRole(roles, PROF):
										msg = "Vous ou les élèves avez déjà cour à ces horraires. "
										if len(taken)==1:
											msg = msg + "\nUn cour trouvé dans l'agenda:\n"
										else:
											msg = msg + "\n" + str(len(taken)) + " cours trouvés dans l'agenda:\n"
										msg = msg + self.getAgenda(taken)
									await message.channel.send(msg)
								elif checkR==False:
									self.writeLog(str(message.author) + "@" + str(message.author.nick) + " from " + str(message.channel) + ": " + str(message.content) + " -> ECHEC NOT PROF" + "\n")
								else:
									self.writeLog(str(message.author) + "@" + str(message.author.nick) + " from " + str(message.channel) + ": " + str(message.content) + " -> ECHEC LAMBDA ERROR" + "\n")
						else:
							await message.channel.send("Tu n'as pas le droit de modifier l'agenda.")
							self.writeLog(str(message.author) + "@" + str(message.author.nick) + " from " + str(message.channel) + " TRY: " + str(message.content) + " WITHOUT RIGHT\n")
					elif words[1] == "del": #-------------------------DEL-----------------------------------------------------------------------------------------------------------------------
						roles = self.getRolesUser(message.author, message.guild)
						if self.hasRole(roles, PROF):# or self.hasRole(roles, DELEG) or self.hasRole(roles, MODO):
							try:
								if words[2].lower()=="*" or words[2].lower()=="all" or words[2].lower()=="tout":
									dltd = self.delEntry("<@!" + str(message.author.id) + ">", dict())
									await message.channel.send("Suppression de:\n" + self.getAgenda(dltd))
									self.writeLog(str(message.author) + "@" + str(message.author.nick) + " from " + str(message.channel) + ": " + str(message.content) + "\n")
								else:
									#await message.channel.send("Effacer entré")
									buf = message.content[11:]
									KWs = self.searchKWs(buf)
									print(KWs)
									param = dict()
									if self.isKW(words[2])==False:
										param['name'] = words[2]
										i=3
										try:
											while self.isKW(words[i])==False:
												param['name'] = param['name'] + " " + words[i]
												i=i+1
										except IndexError:
											pass
									i=0
									while i<len(KWs):
										if i != (len(KWs) - 1):
											a = buf.find(KWs[i][1])
											la = len(KWs[i][1])
											b = buf.find(KWs[i+1][1])
											param[KWs[i][0]] = buf[a+la:-(len(buf)-b)]
										else:
											a = buf.find(KWs[i][1])
											l = len(KWs[i][1])
											param[KWs[i][0]] = buf[a+l:]
										i=i+1
									checkT = True
									timeErrorFrom = dict()
									try:
										if 'start' in param:
											param['start'] = makeTime(param['start'])
										if 'end' in param:
											param['end'] = makeTime(param['end'])
									except TimeError as e:
										checkT = False
										timeErrorFrom = e.getErrorFrom()
									print(param)
									dltd = self.delEntry("<@!" + str(message.author.id) + ">", param)
									if len(dltd)>0 and checkT:
										await message.channel.send("Suppression de:\n" + self.getAgenda(dltd))
										self.writeLog(str(message.author) + "@" + str(message.author.nick) + " from " + str(message.channel) + ": " + str(message.content) + "\n")
									elif checkT==False:
										await message.channel.send("Erreur dans la définition des heures de cours.")
										if 'h' in timeErrorFrom:
											await message.channel.send("Les heures doivent être comprises entre 0 et 23. Vous avez défini l'heure à : " + str(timeErrorFrom['h']))
										if 'm' in timeErrorFrom:
											await message.channel.send("Les minutes doivent être comprises entre 0 et 59. Vous avez défini les minutes à : " + str(timeErrorFrom['m']))
										self.writeLog(str(message.author) + "@" + str(message.author.nick) + " from " + str(message.channel) + ": " + str(message.content) + " -> ECHEC TIMEDEF\n")
									else:
										await message.channel.send("Rien dans l'agenda ne correspond à ces paramètres:\n" + self.makeChampTbl(param))
										self.writeLog(str(message.author) + "@" + str(message.author.nick) + " from " + str(message.channel) + ": " + str(message.content) + "\n -> ECHEC EMPTY")
							except IndexError as e:
								#print(e)
								self.writeLog(str(message.author) + "@" + str(message.author.nick) + " from " + str(message.channel) + ": " + str(message.content) + "\n")
								self.writeLog("ERROR: " + str(e))
								await message.channel.send("Erreur de syntaxe")
								await message.channel.send("Syntaxe correcte:\n/agenda del ")
						else:
							await message.channel.send("Tu n'as pas le droit de modifier l'agenda.")
							self.writeLog(str(message.author) + "@" + str(message.author.nick) + " from " + str(message.channel) + " TRY: " + str(message.content) + " WITHOUT RIGHT\n")
					elif words[1] == "help":	#------------------------------------HELP------------------------------------------------------------------------------------------------------
						#await message.channel.send("Afficher l'aide")
						userRoles = self.getRolesUser(message.author, message.guild)
						dmchan = await message.author.create_dm()
						await dmchan.send(self.getHelp(message.author, message.guild))
						del dmchan
						self.writeLog(str(message.author) + "@" + str(message.author.nick) + " from " + str(message.channel) + ": " + str(message.content) + "\n")
					else:	#------------------------------------------------------Agenda parametre--------------------------------------------------------------------------------------------
						nbr = len(words)-1
						nbrF = len(words)-1
						concern = []
						everyone = False
						i=1
						while i<=nbr:
							everyone = everyone or words[i]=="@everyone" or words[i]=="everyone"
							concern.append(words[i])
							rlID = self.getRoleID(words[i], message.guild)
							if rlID != "":
								concern.append("<@&" + rlID + ">")
								nbrF = nbrF + 1
							i=i+1
						dte = str(date.today())
						rows = self.selectEntry(nbrF, concern, dte, everyone)
						print(concern)
						print(rows)
						agndStr = self.getAgenda(rows)
						answer = "Rien dans l'agenda de " + concern[0]
						if agndStr=="":
							i=1
							while i<len(concern):
								answer = answer + " et " + concern[i]
								i = i+1
							answer = answer + '.'
						else:
							answer = agndStr
						await message.channel.send(answer)
						self.writeLog(str(message.author) + "@" + str(message.author.nick) + " from " + str(message.channel) + ": " + str(message.content) + "\n")
				except AttributeError as e:
					await message.channel.send("Vous devez m'envoyer des messages depuis le serveur")
					print(e)
					if len(words)>1:
						if words[1] == "help":	#------------------------------------HELP------------------------------------------------------------------------------------------------------
							#await message.channel.send("Afficher l'aide")
							hlp = "Commandes disponibles: "
							hlp = hlp + "\n\n`Afficher` votre agenda:\n> **/agenda**"
							hlp = hlp + "\n\n`Afficher` l'agenda d'un groupe:\n> **/agenda** nomDuGroupe"
							hlp = hlp + "\n\n`Afficher` l'agenda de tout le monde:\n> **/agenda everyone**"
							hlp = hlp + "\n\n`Ajouter` un cours dans l'agenda:\n> **/agenda add** Nom du cours **de** heure début **à** heure fin **le** dte **pour** élèves"
							hlp = hlp + "\n\n`Supprimer` un cours de l'agenda:\n> **/agenda del** Nom du cour ***h1*** heureDebut ***h2*** heureFin ***date*** DateDuCour ***pour*** élèves"
							hlp = hlp + "\n\nAfficher une `aide` (simplifiée en DM; détaillée depuis le serveur):\n> **/agenda help**"
							hlp = hlp + "\n\nLes mots en **gras** sont des mots clés nécessaires.\nLes mots en ***gras et italiques*** sont des mots clés facultatifs."
							hlp = hlp + "\n\nVous devez éxecuter les commandes depuis le serveur.\nVous n'avez peut-être pas le droit de toutes les éxecuter"
							hlp = hlp + "\n\nVeuillez signaler tout beug en DM à MrFish#1974."
							await message.channel.send(hlp)
							self.writeLog(str(message.author) + "@None" + " from " + str(message.channel) + ": " + str(message.content) + "\n")
				pass
	def isKW(self, word):
		word = " " + word + " "
		return word==DE[1] or word==A[1] or word==LE[1] or word==POUR[1]
	def getHelp(self, members, guild, firstTime=False):
		userRoles = self.getRolesUser(members, guild)
		if self.hasRole(userRoles, PROF):
			hlp = ""
			if firstTime:
				hlp = ":wave:  Bonjour, je viens tout juste d'arriver sur le serveur " + guild.name + ".\n"
			hlp = hlp + "Je suis un bot qui gère l'agenda de vos cours sur " + guild.name + ". :date:"
			hlp = hlp + "\nJ'ai été créé afin d'éviter que deux cours aient lieu en même temps pour les mêmes personnes."
			hlp = hlp + "\n\nEn tant que *professeur*, vous avez accés à ces commandes: "
			hlp = hlp + "\n\n`Afficher` votre agenda:\n> **/agenda**"
			hlp = hlp + "\n\n`Afficher` l'agenda d'un ou plusieurs groupes:\n> **/agenda** nomDuGroupe1 nomGroupe2 nomGroupe3"
			hlp = hlp + "\n\n`Afficher` l'agenda de tout le monde:\n> **/agenda everyone**"
			hlp = hlp + "\n\n`Ajouter` un cours dans l'agenda:\n> **/agenda add** Nom du cours **de** heure début **à** heure fin **le** date **pour** élèves"
			hlp = hlp + "\nJe vous conseille d'utiliser des @NomDeGroupe pour que les élèves concernés soient notifiés de l'ajout du cours."
			hlp = hlp + "\n\n`Supprimer` un cour de l'agenda:\n> **/agenda del** Nom du cour ***h1*** heureDebut ***h2*** heureFin ***date*** DateDuCour ***pour*** élèves"
			hlp = hlp + "\n\n`Afficher` une `aide` (simplifiée en DM; détaillée depuis le serveur):\n> **/agenda help**"
			hlp = hlp + "\n\nExemple:"
			hlp = hlp + "\n\n`Ajouter` Maths de 10h30 à 12h le 23/03 pour l'ensemble du groupe @TSSI2:"
			hlp = hlp + "\n> **/agenda add** Maths **de** 10h30 **à** 12h **le** 23/03 **pour** @TSSI2"
			hlp = hlp + "\n\n`Supprimer` tous vos cours ayant le nom Chimie:"
			hlp = hlp + "\n> **/agenda del** Chimie"
			hlp = hlp + "\n\n`Supprimer` tous vos cours avec les @TSSI1 qui commence à 9h:"
			hlp = hlp + "\n> **/agenda del** ***pour*** @TSSI1 ***h1*** 9h"
			hlp = hlp + "\n\n`Afficher` l'agenda de @Espagnol et @Spé:"
			hlp = hlp + "\n> **/agenda** @Espagnol @Spé"
			hlp = hlp + "\n\nLes mots en **gras** sont des mots clés, vous devez les écrires dans le même ordre que dans les exemples."
			hlp = hlp + "\nLes mots en ***gras et italiques*** sont des mots clés facultatifs. Vous pouvez les écrire dans l'ordre que vous voulez."
			#hlp = hlp + "\n\nSi vous détectez un bug :bug: , signalez le en DM à MrFish#1974 pour qu'il me répare.  :robot:"
		elif self.hasRole(userRoles, DELEG) or self.hasRole(userRoles, MODO) or self.hasRole(userRoles, AGEND):
			hlp = ""
			if firstTime:
				hlp = ":wave:  Salut, je viens tout juste d'arriver sur le serveur " + guild.name + ".\n"
			hlp = hlp + "Je suis un bot qui gère l'agenda de tes cours sur " + guild.name + ". :date:"
			hlp = hlp + "\nEn tant que *délégué*, tu peux: "
			hlp = hlp + "\n\n`Afficher` ton agenda:\n> **/agenda**"
			hlp = hlp + "\n\n`Afficher` l'agenda d'un ou plusieurs groupes:\n> **/agenda** nomDuGroupe1 nomGroupe2 nomGroupe3"
			hlp = hlp + "\n\n`Afficher` l'agenda de tout le monde:\n> **/agenda everyone**"
			hlp = hlp + "\n\n`Ajouter` un cours dans l'agenda:\n> **/agenda add** Nom du cours **de** heure début **à** heure fin **le** date **pour** élèves **avec** professeur"
			hlp = hlp + "\nJe te conseille d'utiliser des @NomDeGroupe pour que les élèves concernés soient notifiés de l'ajout du cours."
			hlp = hlp + "\nTu dois utiliser le pseudo du professeur."
			#hlp = hlp + "\n\n`Supprimer` un cour de l'agenda:\n> **/agenda del** Nom du cour ***h1*** heureDebut ***h2*** heureFin ***dte*** DateDuCour ***pour*** élèves"
			#hlp = hlp + "\n\n`Afficher` une `aide` (simplifiée en DM; détaillée depuis le serveur):\n> **/agenda help**"
			hlp = hlp + "\n\nExemple:"
			hlp = hlp + "\n\n`Ajouter` Maths avec Mr.Thomas de 10h30 à 12h le 23/03 pour l'ensemble du groupe @TSSI2:"
			hlp = hlp + "\n> **/agenda add** Maths **de** 10h30 **à** 12h **le** 23/03 **pour** @TSSI2 avec Valou#0813"
			#hlp = hlp + "\n\n`Supprimer` tous vos cours ayant le nom Chimie:"
			#hlp = hlp + "\n> **/agenda del** Chimie"
			#hlp = hlp + "\n\n`Supprimer` tous vos cours avec les @TSSI1 qui commence à 9h:"
			#hlp = hlp + "\n> **/agenda del** pour @TSSI1 h1 9h"
			hlp = hlp + "\n\n`Afficher` l'agenda de @Espagnol et @Spé:"
			hlp = hlp + "\n> **/agenda** @Espagnol @Spé"
			hlp = hlp + "\n\nLes mots en **gras** sont des mots clés, tu doit les écrires dans le même ordre que dans les exemples."
			#hlp = hlp + "\n\nSi tu détectes un bug :bug: , signale le en DM à MrFish#1974 pour qu'il me répare.  :robot:"
		else:
			hlp = ""
			if firstTime:
				hlp = ":wave:  Salut, je viens tout juste d'arriver sur le serveur " + guild.name + ".\n"
			hlp = hlp + "Je suis un bot qui gère l'agenda de tes cours sur " + guild.name + ". :date:"
			hlp = hlp + "\nEn tant qu'*élève*, tu peux"
			hlp = hlp + "\n\n`Afficher` ton agenda:\n> **/agenda**"
			hlp = hlp + "\n\n`Afficher` l'agenda d'un ou plusieurs groupes:\n> **/agenda** nomDuGroupe1 nomGroupe2 nomGroupe3"
			hlp = hlp + "\n\n`Afficher` l'agenda de tout le monde:\n> **/agenda everyone**"
			hlp = hlp + "\n\nExemple:"
			hlp = hlp + "\n\n`Afficher` l'agenda de @Espagnol et @Spé:"
			hlp = hlp + "\n> **/agenda** @Espagnol @Spé"
			hlp = hlp + "\n\nLes mots en **gras** sont des mots clés, tu dois les écrires dans le même ordre que dans les exemples."
			#hlp = hlp + "\n\nSi tu détectes un bug :bug: , signale le en DM à MrFish#1974 pour qu'il me répare.  :robot:"
		return hlp
	def makeChampTbl(self, param):
		rtn = "|name\t|\tevent_date\t|\tstart\t|\tend\t|\tconcern\t|\towner|\n|"
		try:
			rtn = rtn + param['name'] + "|"
		except:
			rtn = rtn + "\t\t" + "|"
		try:
			rtn = rtn + param['event_date'] + "|"
		except:
			rtn = rtn + "\t\t" + "|"
		try:
			rtn = rtn + param['start'][:-3] + "|"
		except:
			rtn = rtn + "\t\t" + "|"
		try:
			rtn = rtn + param['end'][:-3] + "|"
		except:
			rtn = rtn + "\t\t" + "|"
		try:
			rtn = rtn + param['concern'] + "|"
		except:
			rtn = rtn + "\t\t" + "|"
		try:
			rtn = rtn + param['owner'] + "|"
		except:
			rtn = rtn + "\t\t" + "|"
		print(rtn)
		return rtn
	def searchKWs(self, string):
		buf = []
		indStr = []
		if string.find(DE[1]) != -1:
			buf.append(DE)
			indStr.append(string.find(DE[1]))
		if string.find(A[1]) != -1:
			buf.append(A)
			indStr.append(string.find(A[1]))
		if string.find(LE[1]) != -1:
			buf.append(LE)
			indStr.append(string.find(LE[1]))
		if string.find(POUR[1]) != -1:
			buf.append(POUR)
			indStr.append(string.find(POUR[1]))
		buf1 = []
		i=0
		for a in indStr:
			buf1.append((i, a))
			i = i + 1
		buf1.sort(key=sortSecond)
		rtn = []
		for b in buf1:
			rtn.append(buf[b[0]])
		#print(buf1)
		#print(rtn)
		return rtn
	def takeBtween(self, string, a, b):
		pass
	def getRoleName(self, roles, roleID):
		rtn = ""
		for role in roles:
			if role.id == roleID:
				rtn = role.name
		return rtn
	def hasRole(self, roles, roleID):	#Retourne true si roleID est dans roles
		rtn = False
		for role in roles:
			if role.id == roleID:
				rtn = True
		return rtn
	def writeLog(self, string):
		self.logFile = open(FILENAME, "a")
		self.logFile.write(str(datetime.now()) + "|" + string)
		self.logFile.close()
	def getNickname(self, user, guild):
		members = guild.members
		rtn = ""
		i=0
		for memb in members:
			if user == memb:
				rtn = memb.nick
		return rtn
	def getRoleID(self, roleName, guild):	#Retourne l'id d'un role a partir de son nom d'un utilisateur => str
		roles = guild.roles
		rtn = ""
		for role in roles:
			if roleName == role.name:
				rtn = str(role.id)
		return rtn
	def getRolesUser(self, user, guild):	#Retourne les roles d'un utilisateur => array
		roles = guild.roles
		rtn = []
		i=0
		while i<len(roles):
			members = roles[i].members
			for memb in members:
				if memb==user:
					rtn.append(roles[i])
			i=i+1
		return rtn
	def getAgenda(self, rows, owner=None):
		if len(rows)==0:
			return ""
		else:
			#for row in rows:
			#	row
			if owner==None:
				agndStr = str(rows[0][0]) + "\t**|**\t" + str(rows[0][1])[-2:] + "/" + str(rows[0][1])[5:-3] + "\t**|**\t" + str(rows[0][2])[:-3] + "\t**|**\t" + str(rows[0][3])[:-3] + "\t**|**\t" + str(rows[0][4]) + "\t**|**\t" + str(rows[0][5])
			else:
				agndStr = str(rows[0][0]) + "\t**|**\t" + str(rows[0][1])[-2:] + "/" + str(rows[0][1])[5:-3] + "\t**|**\t" + str(rows[0][2])[:-3] + "\t**|**\t" + str(rows[0][3])[:-3] + "\t**|**\t" + str(rows[0][4]) + "\t**|**\t" + str(owner)
			i=1
			while i<len(rows):
				if owner==None:
					agndStr = agndStr + '\n' + str(rows[i][0]) + "\t**|**\t" + str(rows[i][1])[-2:] + "/" + str(rows[i][1])[5:-3] + "\t**|**\t" + str(rows[i][2])[:-3] + "\t**|**\t" + str(rows[i][3])[:-3] + "\t**|**\t" + str(rows[i][4]) + "\t**|**\t" + str(rows[i][5])
				else:
					agndStr = agndStr + '\n' + str(rows[i][0]) + "\t**|**\t" + str(rows[i][1])[-2:] + "/" + str(rows[i][1])[5:-3] + "\t**|**\t" + str(rows[i][2])[:-3] + "\t**|**\t" + str(rows[i][3])[:-3] + "\t**|**\t" + str(rows[i][4]) + "\t**|**\t" + str(owner)	
				i=i+1
			return agndStr
	def selectEntryPlus(self, param):
		self.cnx.connect(host = "127.0.0.1", user="root", password="password", database=DATABASE)
		self.db = self.cnx.cursor()
		#RQ = """SELECT name, event_date, start, end, concern, owner FROM devAgenda WHERE (concern='""" + param['concern'] + "' && event_date='" + param['event_date'] + "' && ((start<='" + param['start'] + "' && end>'" + param['end'] + "') || (start<'" + param['end'] + "' && end>='" + param['end'] + "'))) || (owner='""" + param['owner'] + "' && event_date='" + param['event_date'] + "' && ((start<='" + param['start'] + "' && end>'" + param['end'] + "') || (start<'" + param['end'] + "' && end>='" + param['end'] + "')))"
		condiTM = "(((start<='" + param['start'] + "' && end>'" + param['start'] + "') || (start<'" + param['end'] + "' && end>='" + param['end'] + "')) || ((start>'" + param['start'] + "' && start<'" + param['end'] + "') && (end>'" + param['start'] + "' && end<'" + param['end'] + "')))"
		RQ = "SELECT name, event_date, start, end, concern, owner FROM devAgenda WHERE (concern='" + param['concern'] + "' && event_date='" + param['event_date'] + "' && " + condiTM + ") || (owner='" + param['owner'] + "' && event_date='" + param['event_date'] + "' && " + condiTM + ")"
		RQ = RQ + " ORDER BY event_date, start"
		print(RQ)
		self.db.execute(RQ)
		rows = self.db.fetchall()
		self.cnx.commit()
		self.cnx.close()
		return rows
	def selectEntry(self, nbr, concern, dte=None, everyone=False, owner=None):
		self.cnx.connect(host = "127.0.0.1", user="root", password="password", database=DATABASE)
		self.db = self.cnx.cursor()
		if everyone:
			RQ = """SELECT name, event_date, start, end, concern, owner FROM devAgenda"""
			if owner!=None:
				RQ = RQ + " owner = %s"
				RQ = RQ + " && event_date>='" + dte + "'"
				concern.append(owner)
			else:
				RQ = RQ + " WHERE event_date>='" + dte + "'"
			RQ = RQ + " ORDER BY event_date, start"
			print(RQ)
			self.db.execute(RQ)
		else:
			RQ = """SELECT name, event_date, start, end, concern, owner FROM devAgenda WHERE (concern = %s"""
			i=1
			while i<nbr:
				RQ = RQ + """ || concern = %s"""
				i=i+1
			if owner!=None:
				RQ = RQ + " || owner = %s"
				concern.append(owner)
			RQ = RQ + ") && event_date>='" + dte + "'"
			RQ = RQ + " ORDER BY event_date, start"
			print(RQ)
			self.db.execute(RQ, concern)
		rows = self.db.fetchall()
		self.cnx.commit()
		self.cnx.close()
		return rows
	def delEntry(self, owner, param):
		self.cnx.connect(host = "127.0.0.1", user="root", password="password", database=DATABASE)
		self.db = self.cnx.cursor()
		if 'event_date' in param:
			bufDate = param['event_date'].split("/")
			param['event_date'] = str(datetime.now().year) + "-" + bufDate[1] + "-" + bufDate[0]
		conditions = "WHERE owner='" + owner + "'"
		for key,val in param.items():
			conditions = conditions + " && " + key + "='" + val + "'"
		print(conditions)
		RQ = """SELECT name, event_date, start, end, concern, owner FROM devAgenda """ + conditions
		print(RQ)
		self.db.execute(RQ)
		rows = self.db.fetchall()
		self.db.execute("""DELETE FROM devAgenda """ + conditions)
		self.cnx.commit()
		self.cnx.close()
		print(rows)
		return rows
	def addEntry(self, rows):
		self.cnx.connect(host = "127.0.0.1", user="root", password="password", database=DATABASE)
		self.db = self.cnx.cursor()
		self.db.execute("""INSERT INTO devAgenda(name, event_date, start, end, concern, owner) VALUES(%s, %s, %s, %s, %s, %s)""", rows)
		self.cnx.commit()
		self.cnx.close()
	async def close(self):
		try:
			pass
			await self.lastChan.send("Je me déconnecte pour une maintenance.  :wave:")
		except:
			pass
		await super(Botenda, self).close()
		self.writeLog("Botenda stop.\n")
		print("\nClose...")
		

#cnx = mysql.connector.connect(host="127.0.0.1", user="root", password="password", database=DATABASE)
#db = cnx.cursor()
#db.execute("SELECT * FROM devAgenda")
#rows = db.fetchall()
#print(rows)


botenda = Botenda()
botenda.run(TOKEN)

#cnx = mysql.connector.connect(host="127.0.0.1", user="root", password="password", database=DATABASE)
#db = cnx.cursor()
#rows = ['math', '10h', '11h', 'TSSI2']
#db.execute("INSERT INTO devAgenda(name, start, end, concern) VALUES(%s, %s, %s, %s)", rows)
#db.execute("INSERT INTO devAgenda(name, start, end, concern) VALUES(%s, %s, %s, %s)", rows)
#cnx.commit()
##cnx.close()
#print(db.description)