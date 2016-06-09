#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
# Copyright 2015 Timu Eren <timu.eren@gmail.com>
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

from .ad import Ad
from xml.etree import ElementTree as et
from lxml import etree


class VAST(object):
    def __init__(self, settings={}):
        self.ads = []
        self.version = settings.get("version", "3.0")
        self.vast_error_uri = settings.get("vast_error_uri", None)

    def attachAd(self, ad):
        self.ads.append(ad)
        return ad

    def createAd(self, settings):
        ad = Ad(settings)
        self.ads.append(ad)
        return ad

    def cdata(self, param):
        return """<![CDATA[{param}]]>""".format(param=param)

    def add_creatives(self, elem, ad):
        linearCreatives = [c for c in ad.creatives if c.type == "Linear"]
        nonLinearCreatives = [c for c in ad.creatives if c.type == "NonLinear"]
        companionAdCreatives = [c for c in ad.creatives if c.type == "CompanionAd"]

        creativesElem = etree.SubElement(elem, "Creatives")

        for creative in linearCreatives:
            creativeElem = etree.SubElement(creativesElem, "Creative")

            linearOptions = {}
            if creative.skipoffset:
                linearOptions['skipoffset'] = str(creative.skipoffset)

            linearElem = etree.SubElement(creativeElem, "Linear", linearOptions)

            durationElem = etree.SubElement(linearElem, "Duration")
            durationElem.text = str(creative.duration)

            if creative.ad_parameters:
                adParametersOptions = {}
                if creative.ad_parameters.xmlEncoded:
                    adParametersOptions['xmlEncoded'] = str(creative.ad_parameters.xmlEncoded)

                adParametersElem = etree.SubElement(linearElem, "AdParameters", adParametersOptions)
                adParametersElem.text = str(self.cdata(creative.AdParameters.data))

            if creative.trackingEvents:
                trackingEventsElem = etree.SubElement(linearElem, "TrackingEvents")   

                for event in creative.trackingEvents:
                    trackingEventOptions = {"event": str(event.event)}
                    
                    if event.offset:
                        trackingEventOptions["offset"] = str(event.offset)

                    trackingEventElem = etree.SubElement(trackingEventsElem, "Tracking", trackingEventOptions)
                    trackingEventElem.text = str(self.cdata(event.url))

            if creative.videoClicks:
                videoClicksElem = etree.SubElement(linearElem, "VideoClicks")   

                for click in creative.videoClicks:
                    if ad.structure.lower() != 'wrapper' or click['type'] != 'ClickThrough':
                        clickOptions = {};

                        if click['id']:
                            clickOptions['id'] = str(click['id']);

                        clickElem = etree.SubElement(videoClicksElem, click['type'], clickOptions)
                        clickElem.text = str(self.cdata(click['url']))

            if creative.mediaFiles and ad.structure.lower() != 'wrapper':
                mediaFilesElem = etree.SubElement(linearElem, "MediaFiles")

                for media in creative.mediaFiles:
                    mediaFileElem = etree.SubElement(mediaFilesElem, "MediaFile", media["attributes"])
                    mediaFileElem.text = str(self.cdata(media["url"]))

            if len(creative.icons) > 0:
                iconsElem = etree.SubElement(linearElem, "Icons")
                for icon in creative.icons:
                    iconElem = etree.SubElement(iconsElem, "Icon", icon.attributes)
                    
                    with response.Icon(**icon.attributes):
                        attributes = {}
                        if "creativeType" in icon.resource:
                            attributes["creativeType"] = icon.resource["creativeType"]
                        attr = getattr(response, icon.resource["type"])
                        attr(icon.resource["uri"], **attributes)
                        if icon.click or icon.clickThrough:
                            with response.IconClicks:
                                if icon.clickThrough:
                                    response.IconClickThrough(icon.clickThrough)
                                if icon.click:
                                    response.IconClickTraking(icon.click)
                        if icon.view:
                            response.IconViewTracking(icon.view)

        '''
        if len(nonLinearCreatives) > 0:
            for creative in nonLinearCreatives:
                with response.Creative:
                    with response.NonLinearAds:
                        with response.NonLinear(**creative.attributes):
                            for resource in creative.resources:
                                attrs = {}
                                if "creativeType" in resource:
                                    attrs["creativeType"] = resource["creativeType"]
                                element = getattr(response, resource["type"])
                                element(resource["uri"], **attrs)

                            for click in creative.clicks:
                                element = getattr(response, click["type"])
                                element(click["uri"])

                            if creative.AdParameters:
                                response.AdParameters(creative.AdParameters["data"], **{
                                    "xmlEncoded": creative.AdParameters["xmlEncoded"]
                                })
                            if creative.nonLinearClickEvent:
                                response.NonLinearClickTracking(creative.nonLinearClickEvent)

        if len(companionAdCreatives) > 0:
            with response.CompanionAds:
                for creative in companionAdCreatives:
                    with response.Companion(**creative.attributes):
                        for resource in creative.resources:
                            attrs = {}
                            element = getattr(response, resource["type"])
                            if "creativeType" in resource:
                                attrs["creativeType"] = resource["creativeType"]
                            element(resource["uri"], **attrs)
                            if "adParameters" in resource:
                                response.AdParameters(resource["adParameters"]["data"], **{
                                    "xmlEncoded": resource["adParameters"]["xmlEncoded"]
                                })
                        with response.TrakingEvents:
                            for event in creative.trackingEvents:
                                if track:
                                    attrs = {"event": event.event}
                                    if event.offset:
                                        attrs["offset"] = event.offset
                                    response.Tracking(event.url, **attrs)

                        for click in creative.clickThroughs:
                            response.CompanionClickThrough(click)

                        if creative.nonLinearClickEvent:
                            response.CompanionClickTracking(creative.nonLinearClickEvent)
        '''

    def formatXmlResponse(self, response):
        response = etree.tostring(response, pretty_print=True, encoding="UTF-8")
        return response.decode("utf-8")

    def xml(self, options={}):
        root = etree.Element('VAST')
        root.set("version", str(self.version))

        if len(self.ads) == 0 and self.vast_error_uri:
            etree.SubElement(root, "Error", self.cdata(self.vast_error_uri))
            return self.formatXmlResponse(root)

        for ad in self.ads:
            adOptions = { 'id': str(ad.id) }

            if ad.sequence:
                adOptions['sequence'] = str(ad.sequence)

            adElem = etree.SubElement(root, "Ad", adOptions)

            if ad.structure.lower() == 'wrapper':
                wrapperElem = etree.SubElement(adElem, "Wrapper")

                adSystemElem = etree.SubElement(wrapperElem, "AdSystem")
                adSystemElem.text = str(ad.ad_system)

                vastAdTagElem = etree.SubElement(wrapperElem, "VASTAdTagURI")
                vastAdTagElem.text = str(self.cdata(ad.vast_ad_tag_uri))

                if ad.error:
                    adErrorElem = etree.SubElement(wrapperElem, "Error")
                    adErrorElem.text = str(self.cdata(ad.error))

                for impression in ad.impressions:
                    impressionElem = etree.SubElement(wrapperElem, "Impression")
                    impressionElem.text = str(self.cdata(impression["url"]))

                self.add_creatives(wrapperElem, ad)
            else:
                inlineElem = etree.SubElement(adElem, "InLine")

                adSystemElem = etree.SubElement(inlineElem, "AdSystem")
                adSystemElem.text = str(ad.ad_system)

                adTitleElem = etree.SubElement(inlineElem, "AdTitle")
                adTitleElem.text = str(self.cdata(ad.ad_title))

                if ad.description:
                    adDescriptionElem = etree.SubElement(inlineElem, "Description")
                    adDescriptionElem.text = str(self.cdata(ad.description))

                if ad.error:
                    adErrorElem = etree.SubElement(inlineElem, "Error")
                    adErrorElem.text = str(self.cdata(ad.error))

                for impression in ad.impressions:
                    impressionElem = etree.SubElement(inlineElem, "Impression")
                    impressionElem.text = str(self.cdata(impression["url"]))

                self.add_creatives(inlineElem, ad)

                if ad.extensions:
                    extensionsElem = etree.SubElement(inlineElem, "Extensions")

                    for extension in ad.extensions:
                        extensionElem = etree.SubElement(inlineElem, "Extension")

                        if (extension['type']):
                            extensionElem.set("type", extension['type']);

                        extensionElem.append(etree.fromstring(extension['xml']))

        return self.formatXmlResponse(root)
