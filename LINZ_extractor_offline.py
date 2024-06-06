## API Keys, Users may signup for a free account with id.koordinates.com and issue an API key.  
lris_api_key=''
data_api_key=''
basemap_api_key=''

## API Links to layer - please refer to LINZ portal (data.linz.govt.nz) for list of possible raster layers and corresponding index layers.  
## 
lcdb_layer=f"WFS://pagingEnabled='true' preferCoordinatesForWfsT11='false' restrictToRequestBBOX='1' typename='lris.scinfo.org.nz:layer-104400' url='https://lris.scinfo.org.nz/services;key={lris_api_key}/wfs/layer-104400' version='2.0.0'"
##
raster_index=f"WFS://pagingEnabled='true' preferCoordinatesForWfsT11='false' restrictToRequestBBOX='1' typename='data.linz.govt.nz:layer-52112' url='https://data.linz.govt.nz/services;key={data_api_key}/wfs/layer-52112' version='2.0.0'"
raster_layer = f'SmoothPixmapTransform=1&contextualWMSLegend=0&crs=EPSG:2193&dpiMode=7&format=image/png&layers=layer-52109&styles=style%3Dauto&tileMatrixSet=EPSG:2193&url=https://data.linz.govt.nz/services;key={data_api_key}/wmts/1.0.0/layer/52109/WMTSCapabilities.xml'
##

maskRoot='/tmp/dataset/mask/' # Output directory for segmentation masks
clfRoot='/tmp/dataset/img/'   # Output directory for image files
img_count=0       
bb_size=112       # 
out_res=224       # Output png size, spatial resolution is bb_size/out_res
sample_count=5000 # Number of samples
min_distance=10   # Minimum Distance between samples
class_idx=5       # To accomodate future changes to the database

## Preprocessing routine to generate intermediate files

processing.run("native:dissolve", {'INPUT':raster_index ,'FIELD':[],'SEPARATE_DISJOINT':False,'OUTPUT':'ogr:dbname=\'area_mask.gpkg\' table="area_mask" (geom)'})

processing.run("native:intersection", {'INPUT':lcdb_layer,'OVERLAY':'area_mask.gpkg|layername=area_mask','INPUT_FIELDS':[],'OVERLAY_FIELDS':[],'OVERLAY_FIELDS_PREFIX':'','OUTPUT':'ogr:dbname=\'filtered_lcdb.gpkg\' table="filtered_lcdb" (geom)','GRID_SIZE':None})

processing.run("native:dissolve", {'INPUT':'filtered_lcdb.gpkg|layername=filtered_lcdb','FIELD':['Class_2018'],'SEPARATE_DISJOINT':False,'OUTPUT':'ogr:dbname=\'dissolved_lcdb.gpkg\' table="dissolved_lcdb" (geom)'})

processing.run("qgis:randompointsinsidepolygons", {'INPUT':'dissolved_lcdb.gpkg|layername=dissolved_lcdb','STRATEGY':0,'VALUE':sample_count,'MIN_DISTANCE':min_distance,'OUTPUT':'ogr:dbname=\'random_samples.gpkg\' table="random_samples" (geom)'})

processing.run("native:rectanglesovalsdiamonds", {'INPUT':'random_samples.gpkg|layername=random_samples','SHAPE':0,'WIDTH':112,'HEIGHT':112,'ROTATION':0,'SEGMENTS':5,'OUTPUT':'ogr:dbname=\'buffered_samples.gpkg\' table="buffered_samples" (geom)'})

processing.run("native:intersection", {'INPUT':'filtered_lcdb.gpkg|layername=filtered_lcdb','OVERLAY':'buffered_samples.gpkg|layername=buffered_samples','INPUT_FIELDS':[],'OVERLAY_FIELDS':[],'OVERLAY_FIELDS_PREFIX':'','OUTPUT':'ogr:dbname=\'lcdb_of_samples.gpkg\' table="lcdb_of_samples" (geom)','GRID_SIZE':None})


os.makedirs(f'{maskRoot}/',exist_ok=True)
os.makedirs(f'{clfRoot}/',exist_ok=True)
classNumbers=[1,2,5,6,10,12,14,15,16,20,21,22,30,33,40,41,43,44,45,46,47,50,51,52,54,55,56,58,64,68,69,70,71]
masks = QgsVectorLayer('lcdb_of_samples.gpkg')
samples = QgsVectorLayer('buffered_samples.gpkg')
color = QColor(0, 0, 0, 255)

for feature in samples.getFeatures():
    rand_id=feature.id()
    print(f"Processing Random Point: {rand_id}")
    visibleClass={}
    for i in classNumbers:
        visibleClass[i]=0
    feature_masks=masks.getFeatures(QgsFeatureRequest().setFilterExpression(f'"fid_2" = {rand_id}'))
    clipArea_bb=feature.geometry().boundingBox()
    img2= QImage(out_res,out_res, QImage.Format_ARGB32_Premultiplied)
    img2.fill(color.rgba())
    p2 = QPainter()
    p2.begin(img2)
    p2.setRenderHint(QPainter.Antialiasing)
    ms2 = QgsMapSettings()
    ms2.setBackgroundColor(color)
    # set layers to render
    wmsLayer = QgsRasterLayer(raster_layer,'base_map','wms')
    wmsLayer.setExtent(clipArea_bb)
    ms2.setLayers([wmsLayer])
    ms2.setExtent(clipArea_bb)
    ms2.setOutputSize(img2.size())
    render2 = QgsMapRendererCustomPainterJob(ms2, p2)
    render2.start()
    render2.waitForFinished()
    p2.end()
    img_filename = f'{rand_id}'
    img2.save(f'{clfRoot}/{img_filename}.png')

    for feature_mask in feature_masks:
        img_count=img_count+1
        if img_count%1000==0:
            print(f"Generated {img_count} images")
        cls_no=feature_mask.attributes()[class_idx]
        if cls_no==0:
            continue
        cls_img_id=visibleClass[cls_no]
        visibleClass[cls_no]=visibleClass[cls_no]+1
        img_by_class_filename=f'{rand_id}_{cls_no}_{cls_img_id}'
        clipArea=feature_mask.geometry()
        segmask = QgsGeometry.fromRect(clipArea_bb).difference(clipArea)
        color = QColor(0, 0, 0, 255)
        img = QImage(int(outres),int(outres), QImage.Format_ARGB32_Premultiplied)
        img.fill(color.rgba())
        p = QPainter()
        p.begin(img)
        p.setRenderHint(QPainter.Antialiasing)
        ms = QgsMapSettings()
        ms.setBackgroundColor(color)
        wmsLayer = QgsRasterLayer(url_with_params,'base_map','wms')
        wmsLayer.setExtent(clipArea_bb)
        vl=QgsVectorLayer("Polygon","temp","memory")
        vl.setCrs(wmsLayer.crs())
        pr=vl.dataProvider()
        pr.addAttributes([QgsField("name",QVariant.String)])
        vl.updateFields()
        f=QgsFeature()
        f.setGeometry(segmask)
        f.setAttributes([''])
        pr.addFeature(f)
        vl.updateExtents()
        vl.renderer().symbol().setColor(color)
        # set layers to render
        ms.setLayers([vl,wmsLayer])
        ms.setExtent(clipArea_bb)
        ms.setOutputSize(img.size())
        render = QgsMapRendererCustomPainterJob(ms, p)
        render.start()
        render.waitForFinished()
        p.end()
        img.save(f'{maskRoot}/{img_by_class_filename}.png')
    
    ohe=', '.join(map(str,list(visibleClass.values())))
    with open(f'{clfRoot}/{img_filename}.txt', 'w') as f:
        f.write(ohe)
    f.close()
