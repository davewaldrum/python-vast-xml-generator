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

from .creative import Creative


REQUIRED_INLINE = ['id', 'ad_system', 'ad_title']
REQUIRED_WRAPPER = ['id', 'ad_system', 'vast_ad_tag_uri']


def validateSettings(settings, requireds):
    keys = settings.keys()
    for required in requireds:
        if required not in keys:
            raise Exception("Missing required settings: {required}".format(required=required))


def validateInLineSettings(settings):
    validateSettings(settings, REQUIRED_INLINE)


def validateWrapperSettings(settings):
    validateSettings(settings, REQUIRED_WRAPPER)


class Ad(object):
    def __init__(self, settings={}):
        print ("Settings")
        print (settings)
        self.errors = []
        self.surveys = []
        self.impressions = []
        self.creatives = []
        self.extensions = []

        if settings["structure"].lower() == 'wrapper':
            validateWrapperSettings(settings)
            self.vast_ad_tag_uri = settings["vast_ad_tag_uri"]
            self.ad_title = settings.get("ad_title", None)
        else:
            validateInLineSettings(settings)
            self.ad_title = settings["ad_title"]

        self.id = settings["id"]
        self.structure = settings["structure"]
        self.ad_system = settings["ad_system"]

        # optional elements
        self.sequence = settings.get("sequence", None)
        self.error = settings.get("error", None)
        self.description = settings.get("description", None)
        self.avertiser = settings.get("advertiser", None)

        self.pricing = settings.get("pricing", None)

    def attachSurvey(self, settings):
        survey={"url": settings.url}
        if "type" in settings:
            survey["type"] = settings["type"]
        self.surveys.append(survey)

    def attachImpression(self, settings):
        self.impressions.append(settings)
        return self

    def attachCreative(self, creative_type, options):
        creative = Creative(creative_type, options)
        self.creatives.append(creative)
        return creative

    def attachExtension(self, extension_type, xml):
        self.extensions.append({"type": extension_type, "xml": xml})
        return self

