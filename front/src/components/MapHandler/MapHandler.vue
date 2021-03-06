<style src="./mapHandler.css" scoped></style>
<template src="./mapHandler.html"></template>



<script>
import "ol/ol.css";
import Map from "ol/Map";
import View from "ol/View";
//import {defaults as defaultControls, ScaleLine} from 'ol/control';
import TileLayer from "ol/layer/Tile";
import TileWMS from "ol/source/TileWMS";
import VectorLayer from "ol/layer/Vector";
import VectorSource from "ol/source/Vector";
import Feature from "ol/Feature";
import Point from "ol/geom/Point";
import { Style, Circle, Fill, Stroke, RegularShape } from "ol/style";
import GeoJSON from 'ol/format/GeoJSON';

export default {
  name: "MapHandler",
  props: {
    msg: String,
  },
  data: () => ({
    affaire: {},
    affaire_data: {},
    map: null,
    center: { x: null, y: null },
    view: null,
    vectorLayer: null,
    vectorSource: null,
    graphicsLayer: null,
    graphicsLayerSource: null,
    markerStyle: null
  }),

  methods: {
    /**
     * Init map
     */
    initMap: function(center, zoom) {
      //Init marker style
      this.initMarkerStyle();

      //WMS
      var wmsSource = new TileWMS({
        url: process.env.VUE_APP_WMS_URL,
        params: {
          LAYERS: "plan_cadastral_couleur",
          TILED: false
        }
      });

      var wmsLayer = new TileLayer({
        source: wmsSource
      });

      // Vector layer
      this.vectorSource = new VectorSource({
        projection: process.env.VUE_APP_MAP_PROJECTION
      });
      this.vectorLayer = new VectorLayer({
        source: this.vectorSource
      });

      // Graphics layer
      this.initGraphicsLayer();

      // Map layers
      var layers = [wmsLayer, this.vectorLayer, this.graphicsLayer];

      //View
      this.view = new View({
        projection: process.env.VUE_APP_MAP_PROJECTION,
        center: center
          ? [center.x, center.y]
          : process.env.VUE_APP_MAP_DEFAULT_CENTER,
        zoom: zoom
      });

      if (!this.map) {
        this.map = new Map({
          layers: layers,
          target: "mapDiv",
          view: this.view
        });

        //Workaround to draw markers in the good position
        this.makeWorkaroundCanvasTransform();

        // Add click listener
        //this.map.on('click', this.onMapClick);
      } else {
        this.map
          .getView()
          .setCenter(
            center
              ? [center.x, center.y]
              : process.env.VUE_APP_MAP_DEFAULT_CENTER
          );
      }

      // Add marker
      //this.addMarker(center.x, center.y);
    },

    /**
     * Make work around canvas transform
     */
    makeWorkaroundCanvasTransform: function() {
      let _this = this;

      this.vectorSource.once("addfeature", function() {
        _this.setCanvasTransform();
      });
      this.vectorLayer.once("postrender", function() {
        _this.setCanvasTransform();
      });
      window.onresize = function() {
        setTimeout(function() {
          _this.setCanvasTransform();
        }, 500);
      };
      this.view.on("change:resolution", function() {
        _this.setCanvasTransform();
      });
      
      this.map.on("moveend", function() {
        _this.setCanvasTransform();
      });
    },

    /**
     * Handle map click event
     */
    setCanvasTransform: function() {
      var canvasList = document.getElementById("mapDiv").querySelectorAll("canvas");

      if (canvasList && canvasList.length > 1) {
         canvasList.forEach(canvas => {
          canvas.style.transform = "inherit";
         });
      }
    },

    /**
     * Init marker style
     */
    initMarkerStyle: function() {
      this.markerStyle = new Style({
        image: new Circle({
          radius: 7,
          fill: new Fill({ color: "yellow" }),
          stroke: new Stroke({
            color: [0, 0, 0],
            width: 2
          })
        })
      });
    },

    /**
     * Init graphics layer
     */
    initGraphicsLayer: function(){
      this.graphicsLayerSource = new VectorSource({
        projection: process.env.VUE_APP_MAP_PROJECTION
      });
      this.graphicsLayer = new VectorLayer({
        source: this.graphicsLayerSource,
        style: new Style({
          fill: new Fill({ color: '#b3ffff' }),
          stroke: new Stroke({ color: 'red', width: 8 }),
          image: new RegularShape({
            fill: new Fill({ color: 'yellow' }),
            stroke: new Stroke({ color: 'red', width: 4 }),
            points: 4,
            radius: 10,
            radius2: 0,
            angle: Math.PI / 4,
          }),
        }),
        opacity: 0.5
      });
    },

    /**
     * Add graphic to graphics layer
     */
    addGraphic: function(feature){
      this.graphicsLayerSource.clear();      
      const geojsonFormat = new GeoJSON();

      const nGeom = feature.geometry.coordinates.length;

      // Geometry is not empty
      if (nGeom !== 0) {
        this.graphicsLayerSource.addFeatures(geojsonFormat.readFeatures(feature));
        
      // Geometry is empty
      } else if (feature.bbox.length > 1) { 
        const point = new Point(feature.bbox[0], feature.bbox[1]);
        const pointFeature = new Feature(point);
        this.graphicsLayer.addFeatures(pointFeature);
      }

      // Zoom to feature
      if (feature.geometry.type === 'Point') {
        this.view.fit(feature.bbox);
        this.view.setZoom(12);
      } else {
        this.view.fit(feature.bbox, {padding: [50, 50, 50, 50]});
      }
    },


    /**
     * Add marker
     */
    addMarker: function(x, y, zoom) {
      var marker = new Feature({
        geometry: new Point([x, y])
      });
      marker.setStyle(this.markerStyle);
      this.vectorSource.addFeature(marker);

      if(zoom){
        this.view.setCenter([x, y]);
        this.view.setZoom(process.env.VUE_APP_MAP_DEFAULT_AFFAIRE_ZOOM);
      }

    },

    /**
     * Clear markers
     */
    clearMarkers: function() {
      this.vectorSource.clear();
    }


    /**
     * Handle map click event
     */
    /*onMapClick: function(evt) {
      console.log(evt);
      //var viewResolution = this.$refs.view.getResolution();
      var url = this.$refs.wmsSource.getFeatureInfoUrl(
        evt.coordinate,
        null, //viewResolution,
        "EPSG:2056",
        { INFO_FORMAT: "text/html" }
      );
      console.log(url);
    },*/

    /**
     * Handle map mounted event
     */
    /*onMapMounted: function() {
      console.log(this.$refs.map);
    },*/
  },

  mounted: function() {
    this.$root.$emit("mapHandlerReady");
  }
};
</script>

