# Patchwork - automated patch tracking system
# Copyright (C) 2015 Intel Corporation
#
# This file is part of the Patchwork package.
#
# Patchwork is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 2 of the License, or
# (at your option) any later version.
#
# Patchwork is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with Patchwork; if not, write to the Free Software
# Foundation, Inc., 59 Temple Place, Suite 330, Boston, MA  02111-1307  USA

from django.test import Client
import patchwork.tests.test_series as test_series
from patchwork.models import Series, Patch

import hashlib
import re


class SeriesRevisionMboxTest(test_series.Series0010):

    def check_mbox(self, api_url, filename, md5sum):
        response = self.client.get(api_url)
        self.assertEqual(response.status_code, 200)

        s = re.search("filename=([\w\.\-_]+)",
                      response["Content-Disposition"]).group(1)
        self.assertEqual(s, filename)

        # With MySQL, primary keys keep growing and so the actual patch ids
        # will depend on the previous tests run. Make sure to canonicalize
        # the mbox file so we can compare md5sums
        content = re.sub('^X-Patchwork-Id: .*$', 'X-Patchwork-Id: 1',
                         response.content, flags=re.M)
        content_hash = hashlib.md5()
        content_hash.update(content)
        self.assertEqual(content_hash.hexdigest(), md5sum)

    def testSeriesRevisionMbox(self):
        pk = Series.objects.all()[0].pk

        self.check_mbox("/api/1.0/series/%s/revisions/1/mbox/" % pk,
                        'for_each_-intel_-crtc-v2.mbox',
                        '42e2b2c9eeccf912c998be41683f50d7')

    def testPatchMbox(self):
        pk = Patch.objects.all()[2].pk

        self.check_mbox("/api/1.0/patches/%s/mbox/" % pk,
                        '3-4-drm-i915-Introduce-a-for_each_crtc-macro.patch',
                        'b951af09618c6360516f16ed97a30753')
