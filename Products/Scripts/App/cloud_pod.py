#!/usr/bin/env python
# -*- coding: utf-8 -*-
import os
import sys
import re
from enum import Enum

# Base Enum
class PODMODE(Enum):
    Source = 0
    Binary = 1
    HalfBinary = 2

class RTCVERSION(Enum):
    Pre = 0
    Re = 1

# Base Data
ExtcuteDir = "../../../App/".strip()
BaseProjPath = ExtcuteDir + "AgoraEducation" + ".xcodeproj"

SourcePodContent =  """
  # open source libs
  pod 'AgoraClassroomSDK_iOS', :path => '../../open-cloudclass-ios/AgoraClassroomSDK_iOS.podspec'
  pod 'AgoraEduUI', :path => '../../open-cloudclass-ios/AgoraEduUI.podspec'
    
  pod 'AgoraProctorSDK', :path => '../../open-proctor-ios/AgoraProctorSDK.podspec'
  pod 'AgoraProctorUI', :path => '../../open-proctor-ios/AgoraProctorUI.podspec'
    
  pod 'AgoraWidgets', :path => '../../open-apaas-extapp-ios/AgoraWidgets.podspec'
  
  # close source libs
  pod 'AgoraEduCore/Source', :path => '../../cloudclass-ios/AgoraEduCore_Local.podspec'
  pod 'AgoraRte/Source', :path => '../../common-scene-sdk/AgoraRte.podspec'
  
  pod 'AgoraUIBaseViews/Source', :path => '../../apaas-common-libs-ios/AgoraUIBaseViews_Local.podspec'
  pod 'AgoraWidget/Source', :path => '../../apaas-common-libs-ios/AgoraWidget_Local.podspec'
  pod 'AgoraReport', :path => '../../apaas-common-libs-ios/AgoraReport.podspec'
  pod 'AgoraRx', :path => '../../apaas-common-libs-ios/AgoraRx.podspec'

  pod 'MLeaksFinder'
  
  post_install do |installer|
    ## Fix for XCode 12.5
      find_and_replace("Pods/FBRetainCycleDetector/FBRetainCycleDetector/Layout/Classes/FBClassStrongLayout.mm",
        "layoutCache[currentClass] = ivars;", "layoutCache[(id<NSCopying>)currentClass] = ivars;")
  end
end
   """

BinaryPodContent = """
  # open source libs
  pod 'AgoraEduUI/Binary‘, :path => '../../open-cloudclass-ios/AgoraEduUI_Local.podspec'
  pod 'AgoraClassroomSDK_iOS/Binary', :path => '../../open-cloudclass-ios/AgoraClassroomSDK_iOS_Local.podspec'
      
  pod 'AgoraProctorUI/Binary‘, :path => '../../open-proctor-ios/AgoraProctorUI_Local.podspec'
  pod 'AgoraProctorSDK/Binary', :path => '../../open-proctor-ios/AgoraProctorSDK_Local.podspec'
  
  pod 'AgoraWidgets/Binary', :path => '../../open-apaas-extapp-ios/AgoraWidgets_Local.podspec'
  
  # close source libs
  pod 'AgoraEduCore/Binary', :path => '../../cloudclass-ios/AgoraEduCore_Local.podspec'
  pod 'AgoraUIBaseViews/Binary', :path => '../../apaas-common-libs-ios/AgoraUIBaseViews_Local.podspec'
  pod 'AgoraWidget/Binary', :path => '../../apaas-common-libs-ios/AgoraWidget_Local.podspec'
end
"""

PreRtcContent = """
    pod 'AgoraRtcEngine_iOS/RtcBasic', '3.6.2'
"""

RePodContent = """
    pod 'AgoraRtcKit', :path => '../../common-scene-sdk/ReRtc/AgoraRtcKit_Binary.podspec'
"""

LeaksFinderContent = """
def find_and_replace(dir, findstr, replacestr)
  Dir[dir].each do |name|
      text = File.read(name)
      replace = text.gsub(findstr,replacestr)
      if text != replace
          puts "Fix: " + name
          File.open(name, "w") { |file| file.puts replace }
          STDOUT.flush
      end
  end
  Dir[dir + '*/'].each(&method(:find_and_replace))
end
"""

BaseParams = {"podMode": PODMODE.Source,
              "rtcVersion": RTCVERSION.Pre,
              "updateFlag": False}

# Base Functions
def HandlePath(path):
    path = path.strip()
    if os.path.exists(path) == False:
        print  ('Invalid Path!' + path)
        sys.exit(1)

def rtcHandle(lines):
    preRtcPod = "pod 'AgoraRtcEngine_iOS'"
    reRtcPod = "pod 'AgoraRtcKit'"
    preRtcStr = '/PreRtc'
    reRtcStr = '/ReRtc'
    
    if BaseParams["rtcVersion"] == RTCVERSION.Pre:
        print("Replace ReRtc with PreRtc")
        for index,str in enumerate(lines):
            if reRtcStr in str:
                str = str.replace(reRtcStr,preRtcStr)

            if reRtcPod in str:
                str = PreRtcContent

            lines[index] = str
    else:    
        print("Replace PreRtc with ReRtc")
        for index,str in enumerate(lines):
            if preRtcStr in str:
                str = str.replace(preRtcStr,reRtcStr)

            if preRtcPod in str:
                str = RePodContent

            lines[index] = str


def addLeaksFinderFunction(lines):
    if BaseParams["podMode"] != PODMODE.Source:
        return
    
    print("Add function for MLeaksFinder")
    keyword = "target"
    funcName = "def find_and_replace"
    addIndex = -1
    for index,str in enumerate(lines):
        if funcName in str:
            addIndex = -1
            break
        if keyword in str:
            addIndex = index
    
    if addIndex != -1:
        newStr = LeaksFinderContent + "\n" + lines[addIndex]
        lines[addIndex] = newStr


def generatePodfile():
    podFilePath = ExtcuteDir + '%s' % 'Podfile'
    if BaseParams["podMode"] == PODMODE.HalfBinary:
        return

    key = "# open source libs"
    lineNumber = 0
    foundLine = 0
    with open(podFilePath,'r') as f:
        lines = f.readlines()

    for line in lines:
        lineNumber += 1
        if key in line:
            foundLine = lineNumber
            break

    lines = lines[:foundLine]
    if BaseParams["podMode"] == PODMODE.Source:
        lines.append(SourcePodContent)
        addLeaksFinderFunction(lines)
    elif BaseParams["podMode"] == PODMODE.Binary:
        lines.append(BinaryPodContent)

    rtcHandle(lines)
    
    with open(podFilePath,'w') as f:
        f.writelines(lines)
 
def executePod():
    podFilePath = ExtcuteDir + '/%s' % 'Podfile'
    HandlePath(BaseProjPath)
    HandlePath(podFilePath)

    generatePodfile()

    # 改变当前工作目录到指定的路径
    os.chdir(ExtcuteDir)
    print  ('====== pod install log ======')
    os.system('rm -rf Podfile.lock')
    if BaseParams["updateFlag"] == True:
        os.system('pod install --repo-update')
    else:
        os.system('pod install --no-repo-update')

def main():
    paramsLen = len(sys.argv)
    if paramsLen == 1:
        sys.exit(1)
    elif paramsLen == 2:
        # 0为source pod, 1为binary pod
        PodMode = sys.argv[1]
    elif paramsLen == 3:
        PodMode = sys.argv[1]
        # 0为大重构rtc, 1为老版本rtc
        RtcVersion = sys.argv[2]
        BaseParams["rtcVersion"] = RTCVERSION.Re if RtcVersion == "0" else RTCVERSION.Pre
        print  ('Rtc Version: ' + BaseParams["rtcVersion"].name)
    
    BaseParams["podMode"] = PODMODE.Source if PodMode == "0" else PODMODE.Binary
    print  ('Pod Mode: ' + BaseParams["podMode"].name)

    # 若为source pod，开发者模式
#    if BaseParams["podMode"] == PODMODE.Source:
#        modifyFlag = input("Need Update pod repo? Yes: 0, NO: Any\n")
#
#        # 是否需要更新cocoapods repo
#        if modifyFlag == "0":
#            BaseParams["updateFlag"] = True
    
    executePod()

if __name__ == '__main__':
    main()

