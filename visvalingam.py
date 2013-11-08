#!/usr/bin/python
#This script was written by Ralf Klammer, 24.10.2013
#Re-Implementation of Visvalingam-Wyatt-Algorithm
#basically inspired by these descriptions: http://bost.ocks.org/mike/simplify/

#Simple Maths:
#http://de.wikipedia.org/wiki/Dreiecksfl%C3%A4che
#http://www.serlo.org/math/wiki/article/view/abstand-zweier-punkte-berechnen

import math
import json

class VisvalingamSimplification:
	def __init__(self, line_):
		self.line = line_
		self.indizes = []
		for i in xrange(len(self.line)):
			self.indizes.append(i)
		self.enriched = False

		self.json = {}
		self.json['type']='DemoCollection'
		self.json['properties']={}
		self.json['features'] = []
		self.featCounter = 0

	#calculate the area of one triangle
	def getTriangleArea(self, prevP_, P_, nextP_):
		#get the points of the triangle
		prevP = prevP_
		P = P_
		nextP = nextP_
		#calculate the triangle sites
		a = math.sqrt(pow(prevP[0]-P[0],2)+pow(prevP[1]-P[1],2))
		b = math.sqrt(pow(P[0]-nextP[0],2)+pow(P[1]-nextP[1],2))
		c = math.sqrt(pow(nextP[0]-prevP[0],2)+pow(nextP[1]-prevP[1],2))
		#calculate the area of the triangle
		s = (a+b+c)/2.0
		area_0 = s*(s-a)*(s-b)*(s-c)
		area_0 = abs(area_0)
		area=math.sqrt(area_0)
		return area

	#add the area of the triangle to each point
	def enrichPoints(self):
		demoFeat = {}
		demoFeat['type']='DemoFeature'
		demoFeat['properties']={'id':self.featCounter}
		demoFeat['stage']=self.featCounter
		self.featCounter+=1
		featColl = {"type":"FeatureCollection", "features":[]}
		
		#add the 1st point (static)
		demoLine = [self.line[0]]

		minArea = float("infinity");
		for i in range(1,len(self.indizes)-1):
			this = self.indizes[i]
			prev = self.indizes[i-1]
			next = self.indizes[i+1]

			area=self.getTriangleArea(self.line[prev], self.line[this], self.line[next])

			#add the intermediate points (variable)
			demoLine.append(self.line[this])
					
			#define the Triangle-Geometry
			demoTriangleObject = {'type':'Polygon','coordinates':[[self.line[prev], self.line[this], self.line[next],self.line[prev]]]}
			#add the Triangle to the FeatureCollection of the current stage
			featColl["features"].append({"type":"Feature", 'properties':{'area':area}, "geometry":demoTriangleObject})

			#reset minim value for area, if current is smaller than all previous
			if(area<minArea):
				minArea=area
			#save the area of the triangle as 3rd coordinate
			if(len(self.line[this])<3):		#add if it does not exist
				self.line[this].append(area)
			else:							#replace if it does exist already
				self.line[this][2] = area

		#print format(minArea, '.6f')

		#add the last point (static)
		demoLine.append(self.line[len(self.line)-1])
		#define the Line-Geometry (finally)
		demoLineObject = {'type':'LineString', 'coordinates':demoLine}
		#add the Line to the FeatureCollection of the current stage
		featColl["features"].append({"type":"Feature", "properties":[], "geometry":demoLineObject})

		#add the FeatureCollection to the current stage as 'geometries'-object
		demoFeat['geometries']=featColl
		#add the current stage-DemoFeature to the DemoCollection
		self.json['features'].append(demoFeat)
		
		return minArea

	#check for smallest triangles and remove corresponding points from index
	def removeSmallestAreaIndex(self, minArea):
		newIndizes = []
		#print len(self.indizes)
		for i in range(1,len(self.indizes)-1):
			index = self.indizes[i]
			if(self.line[index][2]>minArea):
				newIndizes.append(index)
		newIndizes.insert(0,self.indizes[0])
		newIndizes.append(self.indizes[len(self.indizes)-1])
		self.indizes = newIndizes
		#return newIndizes

	#do Visvalingam-Calculations until only start-& endpoint are left
	def enrichLineString(self):
		while(len(self.indizes)>2):
			minArea_ = self.enrichPoints()
			self.removeSmallestAreaIndex(minArea_)
		self.enriched = True

	#simplify a linestring corresponding to a given tolerance (depends on projection of data)
	def simplifyLineString(self, tolerance_):
		tolerance = tolerance_
		#it is enough to enrich the line once
		if(self.enriched == False):
			self.enrichLineString()
		#build the new line
		newLine = []
		for p in self.line:
			if(len(p)>2):
				if(p[2]>tolerance):
					newLine.append(p)
			else:
				newLine.append(p)
		#print len(newLine)

		json_file=open('demo.json','w');
		json.dump(self.json, json_file);
		json_file.close();

		return newLine
