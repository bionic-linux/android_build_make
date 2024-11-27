
#      http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
#
# This file is included by build/make/core/Makefile, and contains the logic for
# the combined flags files.
#
# TODO: Should we do all of the images in $(IMAGES_TO_BUILD)?
_FLAG_PARTITIONS := product system vendor
# -----------------------------------------------------------------
# Aconfig Flags
# Create a summary file of aconfig flags for each partition
# $(1): built aconfig flags file (out)
# $(2): installed aconfig flags file (out)
# $(3): the partition (in)
# $(4): all input aconfig files (in)
define generate-partition-aconfig-flag-file
$(eval $(strip $(1)): PRIVATE_OUT := $(strip $(1)))
$(eval $(strip $(1)): PRIVATE_IN := $(strip $(4)))
$(strip $(1)): $(ACONFIG) $(strip $(4))
	mkdir -p $$(dir $$(PRIVATE_OUT))
	$$(if $$(PRIVATE_IN), \
		$$(ACONFIG) dump --dedup --format protobuf --out $$(PRIVATE_OUT) \
			--filter container:$(strip $(3))+state:ENABLED \
			--filter container:$(strip $(3))+permission:READ_WRITE \
			$$(addprefix --cache ,$$(PRIVATE_IN)), \
		echo -n > $$(PRIVATE_OUT) \
	)
$(call copy-one-file, $(1), $(2))
endef
# Create a summary file of aconfig flags for all partitions
# $(1): built aconfig flags file (out)
# $(2): installed aconfig flags file (out)
# $(3): all input aconfig files (in)
define generate-global-aconfig-flag-file
$(eval $(strip $(1)): PRIVATE_OUT := $(strip $(1)))
$(eval $(strip $(1)): PRIVATE_IN := $(strip $(3)))
$(strip $(1)): $(ACONFIG) $(strip $(3))
	mkdir -p $$(dir $$(PRIVATE_OUT))
	$$(if $$(PRIVATE_IN), \
		$$(ACONFIG) dump --dedup --format protobuf --out $$(PRIVATE_OUT) \
			$$(addprefix --cache ,$$(PRIVATE_IN)), \
		echo -n > $$(PRIVATE_OUT) \
	)

