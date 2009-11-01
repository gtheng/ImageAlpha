# coding=utf-8
#
#  IAController.py
#  ImageAlpha
#
#  Created by porneL on 21.września.08.
#  Copyright (c) 2008 Lyncroft. All rights reserved.
#

from objc import *
from Foundation import *
import IAImageView
from IACollectionItem import *
from IABackgroundRenderer import *
from IAImage import IAImage

class ImageAlphaDocument(NSDocument):

    zoomedImageView = objc.IBOutlet()
    statusBarView = objc.IBOutlet()
    backgroundsView = objc.IBOutlet()    
    progressBarView = objc.IBOutlet()

    documentImage = None;
    
    def windowNibName(self):
        return u"ImageAlphaDocument"
    
    def windowControllerDidLoadNib_(self, aController):        
        super(ImageAlphaDocument, self).windowControllerDidLoadNib_(aController)
                
        self._startWork();
        
        self.backgroundsView.setContent_([
            IAImageBackgroundRenderer(self._getImage("textures/photoshop","png")),
            IAImageBackgroundRenderer(self._getImage("textures/Rustpattern","jpeg")),
            IAImageBackgroundRenderer(self._getImage("textures/A_MIXRED","jpeg")),
            IAImageBackgroundRenderer(self._getImage("textures/nature71","jpg")),
            IAImageBackgroundRenderer(self._getImage("textures/461223185","jpg")),
            IAImageBackgroundRenderer(self._getImage("textures/G_IRON3","jpg")),
            IAImageBackgroundRenderer(self._getImage("textures/STONE4","jpeg")),
            IAImageBackgroundRenderer(self._getImage("textures/seawaterfull2","jpg")),
            IAImageBackgroundRenderer(self._getImage("textures/461223192","jpg")),
            IAColorBackgroundRenderer(NSColor.redColor()),
            IAColorBackgroundRenderer(NSColor.blueColor()),
            IAColorBackgroundRenderer(NSColor.greenColor()),
        ])
                                
        self.zoomedImageView.window().setAcceptsMouseMovedEvents_(YES);        
        self.zoomedImageView.setBackgroundRenderer_(IAImageBackgroundRenderer(self._getImage("textures/photoshop","png")))
                
        if self.documentImage is not None:
            self.setDisplayImage_(self.documentImage.image())
           # self.setStatusMessage_("Opened " + NSFileManager.defaultManager().displayNameAtPath_(self.documentImage.path));
        else:
            self.setStatusMessage_("To get started, drop PNG image onto main area on the right");
            
        self._endWork();    
    
    def validateUserInterfaceItem_(self,item):
        # I can't find nice way to compare selectors in pyobjc, so here comes __repr__() hack (or non-hack I hope)
        
        
        if self.documentImage is None and item.action().__repr__() in ["'saveDocument:'","'saveDocumentAs:'"]:
            return NO
            
        return super(ImageAlphaDocument, self).validateUserInterfaceItem_(item);
    
    
    def dataOfType_error_(self, typeName, outError):
        if url.isFileURL() or self.documentImage is not None: 
            return (self.documentImage.imageData(), None)
        return (None,None)
    
    def writeToURL_ofType_error_(self, url, typeName, outErorr):
        NSLog("write to %s type %s" % (url.path(), typeName));

        if url.isFileURL() or self.documentImage is not None: 
            data = self.documentImage.imageData();
            if data is not None:                
                return (NSFileManager.defaultManager().createFileAtPath_contents_attributes_(url.path(), data, None), None)
                        
        return (NO,None)
    
    def readFromURL_ofType_error_(self, url, typeName, outError):
        NSLog("Reading file %s" % url.path());
        if not url.isFileURL():            
            return (NO,None)
        return (self.setDocumentImageFromPath_(url.path()),None)
            
    def setStatusMessage_(self,msg):
        NSLog("(status) %s", msg);
        if self.statusBarView is not None: self.statusBarView.setStringValue_(msg);

    def canSetDocumentImageFromPasteboard_(self,pboard):
# disabled until in-memory image support is done    
#        if NSImage.canInitWithPasteboard_(pboard):
#            NSLog("image will handle that");
#            return YES
        
        type = pboard.availableTypeFromArray_([NSFilenamesPboardType]);     
        if type is not None:    
        # FIXME: check for PNGs here
#           filenames = self.filenamesFromPasteboard_(pboard)   
#           NSLog("Filenames %s" % filenames);
#           for f in filenames: 
#               NSLog("drop file %s" % f);
            return YES

    def filenamesFromPasteboard_(self,pboard):
        data = pboard.dataForType_(NSFilenamesPboardType)
        if data is None: return []
        
        filenames, format, errorDescription = NSPropertyListSerialization.propertyListFromData_mutabilityOption_format_errorDescription_(
                    data , kCFPropertyListImmutable, None, None)
        return filenames;           
    
    def setDocumentImageFromPasteboard_(self,pboard):
        type = pboard.availableTypeFromArray_([NSFilenamesPboardType]);     
        if type is not None:    
            filenames = self.filenamesFromPasteboard_(pboard)
            for file in filenames:                    
                if self.setDocumentImageFromPath_(file):
                    return YES

# disabled until in-memory image support is done  
#        if NSImage.canInitWithPasteboard_(pboard):
#            image = NSImage.alloc().initWithPasteboard_(pboard);
#            self.setDocumentImageFromImage_(image)
#            return YES
        
        return NO

    def setDocumentImageFromPath_(self,path):    
        image = NSImage.alloc().initWithContentsOfFile_(path)
        if image is None:
            NSLog("img is none");
            return NO
            
        docimg = IAImage.alloc().init();    
        docimg.setPath_(path);
        docimg.setImage_(image);
        return self.setNewDocumentImage_(docimg);
    
    def setDocumentImageFromImage_(self,image):
        return NO # not supported until iaimage can save temp image
    
#        if self.documentImage is not None:
#            NSLog("That's not supported yet");
#            return NO

#        docimg = IAImage.alloc().init();
#        docimg.setImage_(image)
#        return self.setNewDocumentImage_(docimg);
    
    def setNewDocumentImage_(self,docimg):
        NSLog("new dimage set");
        if self.documentImage is not None:
            NSLog("Destroying document image %s" % self.documentImage);
            self.documentImage.destroy();
        
        NSLog("Setting new document image %s, replaces old %s " % ( docimg, self.documentImage));
        self.setDocumentImage_(docimg);
        docimg.setCallbackWhenImageChanges_(self);
        self.setDisplayImage_(docimg.image());
        if self.zoomedImageView is not None: self.zoomedImageView.zoomToFill()
        return YES
    
    def setDocumentImage_(self,docimg):
        self.documentImage = docimg;
    
    def setDisplayImage_(self,image):
        if self.zoomedImageView is None or self.backgroundsView is None: return;
        self.zoomedImageView.setImage_(image)
        self.backgroundsView.setImage_(image)
        self.backgroundsView.setSelectable_(YES if image is not None else NO);
        NSLog("Set new display image %s" % image);
    
    def imageChanged(self):
        self.setDisplayImage_(self.documentImage.image());
        data = self.documentImage.imageData()
        self.updateProgressbar()
        if data is not None: self.setStatusMessage_("Image size: %d bytes" % data.length())
    
    def _getImage(self,name,ext="png"):
        path = NSBundle.mainBundle().resourcePath().stringByAppendingPathComponent_(name).stringByAppendingPathExtension_(ext);
        image = NSImage.alloc().initWithContentsOfFile_(path);
        if image is None:
            NSLog("Failed to load %s " % name);
        return image
    
    _busyLevel = 0   
    
    def _startWork(self):        
        self._busyLevel += 1        
        self.updateProgressbar()

    def _endWork(self):
        self._busyLevel -= 1
        self.updateProgressbar()
        
    def updateProgressbar(self):
        if self.progressBarView is None: return
        
        isBusy = self._busyLevel > 0;        
        if not isBusy and self.documentImage is not None and self.documentImage.isBusy(): isBusy = True
        
        if isBusy:
            self.progressBarView.startAnimation_(self);
        else:
            self.progressBarView.stopAnimation_(self);
        
    @objc.IBAction
    def next_(self,action):
        self.setDocumentImageFromPath_(NSBundle.mainBundle().pathForResource_ofType_("bg", "png"));
        
    @objc.IBAction
    def prev_(self,action):
        pass

    @objc.IBAction
    def revert_(self,action):
        pass
        