from rtree import index
from geoip import geolite2

class NearestIps(object):
	"""docstring for NearestIps"""
	RtreeDataStructure = index.Index()
	counter = 0
	@staticmethod
	def populateRtree(listOfIPs):
		for oneIp in listOfIPs:
			cooridinatesOfIp = NearestIps.calulateCoordinatesFromIP(oneIp)
			minx = min(cooridinatesOfIp[0],cooridinatesOfIp[0]+1)
			maxx = max(cooridinatesOfIp[0],cooridinatesOfIp[0]+1)
			miny = min(cooridinatesOfIp[1],cooridinatesOfIp[1]+1)
			maxy = max(cooridinatesOfIp[1],cooridinatesOfIp[1]+1)
			print minx, maxx, miny, maxy
			NearestIps.RtreeDataStructure.insert(NearestIps.counter,(minx,maxx,miny,maxy),obj = oneIp)

			NearestIps.counter = NearestIps.counter +1
	@staticmethod
	def calulateCoordinatesFromIP(ipInput):
		match = geolite2.lookup(ipInput)
		return match.location
	@staticmethod
	def findnthNearest(ipInput,n):
		cooridinatesOfIp = NearestIps.calulateCoordinatesFromIP(ipInput)
		minx = min(cooridinatesOfIp[0],cooridinatesOfIp[0]+1)
		maxx = max(cooridinatesOfIp[0],cooridinatesOfIp[0]+1)
		miny = min(cooridinatesOfIp[1],cooridinatesOfIp[1]+1)
		maxy = max(cooridinatesOfIp[1],cooridinatesOfIp[1]+1)
		return list(NearestIps.RtreeDataStructure.nearest((minx,maxx,miny,maxy), n,objects =False))

listi = ["182.0.0.11","203.0.0.1","150.0.9.1"]
NearestIps.populateRtree(listi)
print NearestIps.findnthNearest("182.0.0.12",0)



# printing all values
# does not work for 18.0.0.1
