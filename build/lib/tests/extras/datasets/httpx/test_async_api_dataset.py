# Copyright 2020 QuantumBlack Visual Analytics Limited
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
# http://www.apache.org/licenses/LICENSE-2.0
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND,
# EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES
# OF MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE, AND
# NONINFRINGEMENT. IN NO EVENT WILL THE LICENSOR OR OTHER CONTRIBUTORS
# BE LIABLE FOR ANY CLAIM, DAMAGES, OR OTHER LIABILITY, WHETHER IN AN
# ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF, OR IN
# CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.
#
# The QuantumBlack Visual Analytics Limited ("QuantumBlack") name and logo
# (either separately or in combination, "QuantumBlack Trademarks") are
# trademarks of QuantumBlack. The License does not grant you any right or
# license to the QuantumBlack Trademarks. You may not use the QuantumBlack
# Trademarks or any confusingly similar mark as a trademark for your product,
#     or use the QuantumBlack Trademarks in any other manner that might cause
# confusion in the marketplace, including but not limited to in advertising,
# on websites, or on software.
#
# See the License for the specific language governing permissions and
# limitations under the License.

import io

# pylint: disable=no-member
import PIL
import pytest
from kedro.io.core import DataSetError

from pipelinex import AsyncAPIDataSet as APIDataSet


def test_successfully_load_with_content_response():
    api_data_set = APIDataSet(
        url="https://raw.githubusercontent.com/quantumblacklabs/kedro/develop/img/kedro_banner.png",
        method="GET",
        attribute="content",
    )
    content = api_data_set.load()
    assert content[1:4] == b"PNG"  # part of PNG file signature


def test_successfully_load_with_response_itself():
    api_data_set = APIDataSet(
        url="https://raw.githubusercontent.com/quantumblacklabs/kedro/develop/img/kedro_banner.png",
        method="GET",
        attribute="",
    )
    response = api_data_set.load()
    content = response.content
    assert content[1:4] == b"PNG"  # part of PNG file signature


def test_attribute_not_found():
    attribute = "wrong_attribute"
    api_data_set = APIDataSet(
        url="https://raw.githubusercontent.com/quantumblacklabs/kedro/develop/img/kedro_banner.png",
        method="GET",
        attribute=attribute,
    )
    pattern = r"Response has no attribute: {}".format(attribute)

    with pytest.raises(DataSetError, match=pattern):
        api_data_set.load()


foobar_prefix = "https://raw.githubusercontent.com/"
foo_image_url = foobar_prefix + "quantumblacklabs/kedro/develop/img/kedro_banner.png"
bar_image_url = (
    foobar_prefix + "quantumblacklabs/kedro/develop/img/pipeline_visualisation.png"
)


def test_successfully_load_from_url_dict_with_content_response():
    api_data_set = APIDataSet(
        url={"foo_image.png": foo_image_url, "bar_image.png": bar_image_url},
        method="GET",
        attribute="content",
        pool_config={
            foobar_prefix: {
                "pool_connections": 1,
                "pool_maxsize": 1,
                "max_retries": 0,
                "pool_block": False,
            }
        },
    )
    content_dict = api_data_set.load()
    assert isinstance(content_dict, dict)
    for content in content_dict.values():
        assert content[1:4] == b"PNG"  # part of PNG file signature


def test_successfully_load_from_url_list_with_content_response():
    api_data_set = APIDataSet(
        url=[foo_image_url, bar_image_url],
        method="GET",
        attribute="content",
        pool_config={
            foobar_prefix: {
                "pool_connections": 1,
                "pool_maxsize": 1,
                "max_retries": 0,
                "pool_block": False,
            }
        },
    )
    content_list = api_data_set.load()
    assert isinstance(content_list, list)
    for content in content_list:
        assert content[1:4] == b"PNG"  # part of PNG file signature


def test_successfully_load_from_url_list_with_content_response_by_call():
    api_data_set = APIDataSet(
        pool_config={
            foobar_prefix: {
                "pool_connections": 1,
                "pool_maxsize": 1,
                "max_retries": 0,
                "pool_block": False,
            }
        },
    )
    content_list = api_data_set(
        url=[foo_image_url, bar_image_url],
        method="GET",
        attribute="content",
    )
    assert isinstance(content_list, list)
    for content in content_list:
        assert content[1:4] == b"PNG"  # part of PNG file signature


def test_successfully_load_from_url_list_with_content_response_by_call_twice():
    api_data_set = APIDataSet(
        pool_config={
            foobar_prefix: {
                "pool_connections": 1,
                "pool_maxsize": 1,
                "max_retries": 0,
                "pool_block": False,
            }
        },
    )
    content_list = api_data_set(
        url=[foo_image_url, bar_image_url],
        method="GET",
        attribute="content",
    )
    assert isinstance(content_list, list)
    for content in content_list:
        assert content[1:4] == b"PNG"  # part of PNG file signature

    content_list = api_data_set(
        url=[foo_image_url, bar_image_url],
        method="GET",
        attribute="content",
    )
    assert isinstance(content_list, list)
    for content in content_list:
        assert content[1:4] == b"PNG"  # part of PNG file signature


def test_successfully_load_from_url_list_with_transforms_by_call():
    api_data_set = APIDataSet(
        pool_config={
            foobar_prefix: {
                "pool_connections": 1,
                "pool_maxsize": 1,
                "max_retries": 0,
                "pool_block": False,
            }
        },
        transforms=[io.BytesIO, PIL.Image.open],
    )
    image_list = api_data_set(
        url=[foo_image_url, bar_image_url],
        method="GET",
        attribute="content",
    )
    for image in image_list:
        assert isinstance(image, PIL.Image.Image)
