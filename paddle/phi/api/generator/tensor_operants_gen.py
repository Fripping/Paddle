# Copyright (c) 2023 PaddlePaddle Authors. All Rights Reserved.
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

import argparse

import yaml
from api_gen import ForwardAPI

inplace_out_type_map = {
    "Tensor": "Tensor&",
    "std::vector<Tensor>": "std::vector<Tensor>&",
}

inplace_optional_out_type_map = {
    "Tensor": "paddle::optional<Tensor>&",
    "std::vector<Tensor>": "paddle::optional<std::vector<Tensor>>&",
}

indent = "  "

# E.g.: Prim uses `elementwise_pow + fill_constant` to replace `pow`, so that we use this map to generate the `pow` signature when iterating over `elementwise_pow` API.
specific_ops_map = {"elementwise_pow": "pow"}


operants_base_include = """// Generated by paddle/phi/api/generator/tensor_operants_gen.py

#pragma once

#include "paddle/phi/api/include/tensor.h"
#include "paddle/phi/common/scalar.h"
#include "paddle/phi/common/int_array.h"

"""

operants_base_start = """
namespace paddle {

namespace operants {

using Tensor = paddle::Tensor;
using Scalar = paddle::experimental::Scalar;
using IntArray = paddle::experimental::IntArray;

class TensorOperantsBase {
 public:
  virtual ~TensorOperantsBase() = default;

  virtual Tensor add(const Tensor& x, const Scalar& y) = 0;

  virtual Tensor divide(const Tensor& x, const Scalar& y) = 0;

  virtual Tensor multiply(const Tensor& x, const Scalar& y) = 0;

  virtual Tensor subtract(const Tensor& x, const Scalar& y) = 0;

  virtual Tensor add(const Scalar& x, const Tensor& y) = 0;

  virtual Tensor divide(const Scalar& x, const Tensor& y) = 0;

  virtual Tensor multiply(const Scalar& x, const Tensor& y) = 0;

  virtual Tensor subtract(const Scalar& x, const Tensor& y) = 0;

  virtual Tensor pow(const Tensor& x, const Tensor& y) = 0;

  virtual Tensor pow(const Tensor& x, const Scalar& y) = 0;
"""


operants_base_end = """};

}  // namespace operants
}  // namespace paddle

"""

tensor_api_source_include = """// Generated by paddle/phi/api/generator/tensor_operants_gen.py

#include "paddle/phi/api/include/tensor.h"

#include "paddle/phi/api/include/operants_manager.h"

"""

tensor_api_source_start = """
namespace paddle {

Tensor Tensor::operator+(const Tensor &other) const {
  return add(other);
}

Tensor Tensor::operator-(const Tensor &other) const {
  return subtract(other);
}

Tensor Tensor::operator*(const Tensor &other) const {
  return multiply(other);
}

Tensor Tensor::operator/(const Tensor &other) const {
  return divide(other);
}

Tensor Tensor::operator+(const Scalar &other) const {
  return add(other);
}

Tensor Tensor::operator-(const Scalar &other) const {
  return subtract(other);
}

Tensor Tensor::operator*(const Scalar &other) const {
  return multiply(other);
}

Tensor Tensor::operator/(const Scalar &other) const {
  return divide(other);
}

Tensor Tensor::add(const Scalar& y) const {
  return paddle::OperantsManager::Instance().add(static_cast<const Tensor &>(*this), y);
}

Tensor Tensor::divide(const Scalar& y) const {
  return paddle::OperantsManager::Instance().divide(static_cast<const Tensor &>(*this), y);
}

Tensor Tensor::multiply(const Scalar& y) const {
  return paddle::OperantsManager::Instance().multiply(static_cast<const Tensor &>(*this), y);
}

Tensor Tensor::subtract(const Scalar& y) const {
  return paddle::OperantsManager::Instance().subtract(static_cast<const Tensor &>(*this), y);
}

Tensor Tensor::operator<(const Tensor &other) const {
  return less_than(other);
}

Tensor Tensor::operator<=(const Tensor &other) const {
  return less_equal(other);
}

Tensor Tensor::operator==(const Tensor &other) const {
  return equal(other);
}

Tensor Tensor::operator!=(const Tensor &other) const {
  return not_equal(other);
}

Tensor Tensor::operator>(const Tensor &other) const {
  return greater_than(other);
}

Tensor Tensor::operator>=(const Tensor &other) const {
  return greater_equal(other);
}

Tensor Tensor::operator-() const {
  return scale(-1.0, 0.0, true);
}

Tensor Tensor::operator~() const {
  return bitwise_not();
}

Tensor Tensor::operator&(const Tensor &other) const {
  return bitwise_and(other);
}

Tensor Tensor::operator|(const Tensor &other) const {
  return bitwise_or(other);
}

Tensor Tensor::operator^(const Tensor &other) const {
  return bitwise_xor(other);
}

Tensor Tensor::pow(const Tensor& y) const {
  return paddle::OperantsManager::Instance().pow(static_cast<const Tensor &>(*this), y);
}

Tensor Tensor::pow(const Scalar& y) const {
  return paddle::OperantsManager::Instance().pow(static_cast<const Tensor &>(*this), y);
}

PADDLE_API Tensor operator+(const Scalar& x, const Tensor& y) {
  return paddle::OperantsManager::Instance().add(x, y);
}

PADDLE_API Tensor operator-(const Scalar& x, const Tensor& y) {
  return paddle::OperantsManager::Instance().subtract(x, y);
}

PADDLE_API Tensor operator*(const Scalar& x, const Tensor& y) {
  return paddle::OperantsManager::Instance().multiply(x, y);
}

PADDLE_API Tensor operator/(const Scalar& x, const Tensor& y) {
  return paddle::OperantsManager::Instance().divide(x, y);
}
"""


tensor_api_source_end = """
}  // namespace paddle

"""


operants_header_include = """// Generated by paddle/phi/api/generator/tensor_operants_gen.py

#pragma once

#include "paddle/phi/api/include/operants_base.h"
#include "paddle/phi/api/include/tensor.h"
#include "paddle/phi/common/scalar.h"
#include "paddle/phi/common/int_array.h"
#include "paddle/common/macros.h"

"""

operants_header_start = """
namespace paddle {

namespace operants {

using Scalar = paddle::experimental::Scalar;
using IntArray = paddle::experimental::IntArray;

class PhiTensorOperants : public TensorOperantsBase {
 private:
  DISABLE_COPY_AND_ASSIGN(PhiTensorOperants);

 public:
  PhiTensorOperants() = default;

  Tensor add(const Tensor& x, const Scalar& y);

  Tensor subtract(const Tensor& x, const Scalar& y);

  Tensor multiply(const Tensor& x, const Scalar& y);

  Tensor divide(const Tensor& x, const Scalar& y);

  Tensor add(const Scalar& x, const Tensor& y);

  Tensor subtract(const Scalar& x, const Tensor& y);

  Tensor multiply(const Scalar& x, const Tensor& y);

  Tensor divide(const Scalar& x, const Tensor& y);

  Tensor pow(const Tensor& x, const Tensor& y);

  Tensor pow(const Tensor& x, const Scalar& y);

"""


operants_header_end = """};

}  // namespace operants
}  // namespace paddle

"""


operants_source_include = """// Generated by paddle/phi/api/generator/tensor_operants_gen.py

#include "paddle/phi/api/include/tensor_operants.h"

#include "paddle/phi/api/include/api.h"

"""


operants_source_start = """
namespace paddle {

namespace operants {

Tensor PhiTensorOperants::add(const Tensor& x, const Scalar& y) {
  return paddle::experimental::add(x, paddle::experimental::full_like(x, y));
}

Tensor PhiTensorOperants::subtract(const Tensor& x, const Scalar& y) {
  return paddle::experimental::subtract(x, paddle::experimental::full_like(x, y));
}

Tensor PhiTensorOperants::multiply(const Tensor& x, const Scalar& y) {
  return paddle::experimental::scale(x, y, 0.0f, true);
}

Tensor PhiTensorOperants::divide(const Tensor& x, const Scalar& y) {
  return paddle::experimental::divide(x, paddle::experimental::full_like(x, y));
}

Tensor PhiTensorOperants::add(const Scalar& x, const Tensor& y) {
  return paddle::experimental::add(paddle::experimental::full_like(y, x), y);
}

Tensor PhiTensorOperants::subtract(const Scalar& x, const Tensor& y) {
  return paddle::experimental::subtract(paddle::experimental::full_like(y, x), y);
}

Tensor PhiTensorOperants::multiply(const Scalar& x, const Tensor& y) {
  return paddle::experimental::scale(y, x, 0.0f, true);
}

Tensor PhiTensorOperants::divide(const Scalar& x, const Tensor& y) {
  return paddle::experimental::divide(paddle::experimental::full_like(y, x), y);
}

Tensor PhiTensorOperants::pow(const Tensor& x, const Tensor& y) {
  return paddle::experimental::elementwise_pow(x, y);
}

Tensor PhiTensorOperants::pow(const Tensor& x, const Scalar& y) {
  return paddle::experimental::elementwise_pow(x, paddle::experimental::full_like(x, y));
}
"""


operants_source_end = """
}  // namespace operants
}  // namespace paddle

"""


operants_manager_header_include = """// Generated by paddle/phi/api/generator/tensor_operants_gen.py

#pragma once

#include "paddle/phi/api/include/operants_base.h"
#include "paddle/phi/api/include/tensor.h"
#include "paddle/phi/common/scalar.h"
#include "paddle/phi/common/int_array.h"
#include "paddle/common/macros.h"
#include "paddle/utils/test_macros.h"

"""

operants_manager_header_start = """
namespace paddle {

using Tensor = paddle::Tensor;
using Scalar = paddle::experimental::Scalar;
using IntArray = paddle::experimental::IntArray;
using TensorOperantsBase = paddle::operants::TensorOperantsBase;

/**
 * [ Why need OperantsManager? ]
 *
 * Ideally, overloading tensor operators should call Tensor API directly.
 * However, we faced two problems:
 *
 * 1. Support multiple modes: Tensor operator overloading needs to support
 * [static mode / autograd mode / custom operator mode] at the same time.
 *
 * 2. Decouple phi and fluid: Tensor belongs to the phi library, but it relies
 * upon functions in fluid when overloading Tensor operators.
 *
 * We design OperantsManager to solve these two problems:
 *
 * 1. use `FLAGS_tensor_operants_mode` to handle overloading mode, set this flag
 * at the entry point of each mode:
 *
 * - FLAGS_tensor_operants_mode = "static": at the construction function of
 * `CompositeGradOpMakerBase`.
 * - FLAGS_tensor_operants_mode = "eager": at the beginning of dygraph_function.
 * - FLAGS_tensor_operants_mode = "phi": at the beginning of the
 * `eager_api_run_custom_op` function in eager mode and at the beginning of
 * calling kernels in static mode.
 *
 * In order to guarantee the performance, OperantsManager holds three pointers
 * to identify each mode respectively.
 *
 * 2. Decouple phi with the help of the polymorphism mechanism,
 * TensorOperantsBase derives three child classes: PhiTensorOperants,
 * EagerTensorOperants, and StaticTensorOperants. We set eager and static tensor
 * operants at the fluid library and set phi operants at the phi library.
 *
 */
class TEST_API OperantsManager {
 private:
  OperantsManager() = default;
  DISABLE_COPY_AND_ASSIGN(OperantsManager);

 public:
  std::unique_ptr<TensorOperantsBase> eager_operants{nullptr};
  std::unique_ptr<TensorOperantsBase> static_operants{nullptr};
  std::unique_ptr<TensorOperantsBase> phi_operants{nullptr};

 public:
  static OperantsManager& Instance();

  Tensor add(const Tensor& x, const Scalar& y);

  Tensor subtract(const Tensor& x, const Scalar& y);

  Tensor multiply(const Tensor& x, const Scalar& y);

  Tensor divide(const Tensor& x, const Scalar& y);

  Tensor add(const Scalar& x, const Tensor& y);

  Tensor subtract(const Scalar& x, const Tensor& y);

  Tensor multiply(const Scalar& x, const Tensor& y);

  Tensor divide(const Scalar& x, const Tensor& y);

  Tensor pow(const Tensor& x, const Tensor& y);

  Tensor pow(const Tensor& x, const Scalar& y);

"""


operants_manager_header_end = """};

}  // namespace paddle

"""


operants_manager_source_include = """// Generated by paddle/phi/api/generator/tensor_operants_gen.py

#include "paddle/phi/api/include/operants_manager.h"

#include "glog/logging.h"
#include "paddle/phi/core/enforce.h"
#include "paddle/common/errors.h"
#include "paddle/common/flags.h"

"""


operants_manager_source_start = """
COMMON_DECLARE_string(tensor_operants_mode);

namespace paddle {

OperantsManager& OperantsManager::Instance() {
  static OperantsManager g_op_manager;
  return g_op_manager;
}
"""


operants_manager_source_end = """
}  // namespace paddle

"""


class OperantsAPI(ForwardAPI):
    def __init__(self, api_item_yaml, prims=()):
        super().__init__(api_item_yaml)
        self.is_prim_api = False
        if self.get_api_func_name() in prims:
            self.is_prim_api = True

    def gene_operants_base(self):
        api_func_name = self.get_api_func_name()
        if api_func_name[-1] != '_':
            return f"""
{indent}virtual {self.get_return_type()} {api_func_name}({self.get_declare_args()}) = 0;
"""
        else:
            return f"""
{indent}virtual {self.get_return_type(inplace_flag=True)} {api_func_name}({self.get_declare_args(inplace_flag=True)}) = 0;
"""

    def get_declare_args_without_first_tensor(self, inplace_flag=False):
        func_name = self.get_api_func_name()
        declare_args = self.get_input_tensor_args(inplace_flag)
        assert (
            len(declare_args) >= 1
        ), f"Error! Api {func_name} has no Tensor inputs"
        first_input_type = " ".join(declare_args[0].split(" ")[:-1])
        # NOTE(HongyuJia): Do not consider "const paddle::optional<Tensor>&"
        assert (
            first_input_type == "const Tensor&"
        ), f"Error! The first argument of Tensor Api {func_name} must be Tensor, but received {first_input_type}"
        for name in self.attrs['names']:
            default_value = ''
            if self.attrs['attr_info'][name][1] is not None:
                default_value = ' = ' + self.attrs['attr_info'][name][1]
            declare_args.append(
                self.attrs['attr_info'][name][0] + ' ' + name + default_value
            )
        # remove first Tensor argument
        return ", ".join(declare_args[1:])

    def get_define_args_without_first_tensor(self, inplace_flag=False):
        func_name = self.get_api_func_name()
        define_args = self.get_input_tensor_args(inplace_flag)
        assert (
            len(define_args) >= 1
        ), f"Error! Api {func_name} has no Tensor inputs"
        first_input_type = " ".join(define_args[0].split(" ")[:-1])
        # NOTE(HongyuJia): Do not consider "const paddle::optional<Tensor>&"
        assert (
            first_input_type == "const Tensor&"
        ), f"Error! The first argument of Tensor Api {func_name} must be Tensor, but received {first_input_type}"
        for name in self.attrs['names']:
            define_args.append(self.attrs['attr_info'][name][0] + ' ' + name)
        # remove first Tensor argument
        return ", ".join(define_args[1:])

    def gene_tensor_api_implementation(self):
        func_name = self.get_api_func_name()
        assert (
            len(self.inputs['names']) >= 1
        ), f"Error! Api {func_name} has no Tensor inputs"
        # remove first Tensor argument
        func_args = self.inputs['names'][1:] + self.attrs['names']
        if len(func_args) > 0:
            func_args_code = ", ".join([""] + func_args)
        else:
            func_args_code = ""
        # func decalaration
        if func_name[-1] != '_':
            return f"""
{self.get_return_type()} Tensor::{func_name}({self.get_define_args_without_first_tensor()}) const {{
{indent}return paddle::OperantsManager::Instance().{func_name}(static_cast<const Tensor &>(*this){func_args_code});
}}
"""
        else:
            return f"""
{self.get_return_type(inplace_flag=True)} Tensor::{func_name}({self.get_define_args_without_first_tensor(inplace_flag=True)}) const {{
{indent}return paddle::OperantsManager::Instance().{func_name}(static_cast<const Tensor &>(*this){func_args_code});
}}

"""

    def gene_operants_declaration(self):
        api_func_name = self.get_api_func_name()
        if api_func_name[-1] != '_':
            return f"""
{indent}{self.get_return_type()} {api_func_name}({self.get_declare_args()});
"""
        else:
            return f"""
{indent}{self.get_return_type(inplace_flag=True)} {api_func_name}({self.get_declare_args(inplace_flag=True)});
"""

    def gene_operants_implementation(self):
        func_name = self.get_api_func_name()
        func_args = self.inputs['names'] + self.attrs['names']
        func_args_code = ", ".join(func_args)
        # func decalaration
        if func_name[-1] != '_':
            return f"""
{self.get_return_type()} PhiTensorOperants::{func_name}({self.get_define_args()}) {{
{indent}return paddle::experimental::{func_name}({func_args_code});
}}
"""
        else:
            return f"""
{self.get_return_type(inplace_flag=True)} PhiTensorOperants::{func_name}({self.get_define_args(inplace_flag=True)}) {{
{indent}return paddle::experimental::{func_name}({func_args_code});
}}

"""

    def gene_operants_manager_code(self, is_specific_op=False):
        func_name = self.get_api_func_name()
        if is_specific_op:
            func_name = specific_ops_map[func_name]
        func_args = self.inputs['names'] + self.attrs['names']
        func_args_code = ", ".join(func_args)
        return f"""
  if (FLAGS_tensor_operants_mode == "eager") {{
    PADDLE_ENFORCE_NE(
        this->eager_operants.get(),
        nullptr,
        common::errors::Unavailable("The eager_operants pointer of "
                                 "OperantsManager is not initialized"));
    VLOG(4) << "OperantsManager reusing eager mode API ::{func_name}_ad_func";
    return this->eager_operants->{func_name}({func_args_code});
  }} else if (FLAGS_tensor_operants_mode == "static") {{
    PADDLE_ENFORCE_NE(
        this->static_operants.get(),
        nullptr,
        common::errors::Unavailable("The static_operants pointer of "
                                 "OperantsManager is not initialized"));
    VLOG(4) << "OperantsManager reusing static mode API paddle::prim::{func_name}<DescTensor>";
    return this->static_operants->{func_name}({func_args_code});
  }} else if (FLAGS_tensor_operants_mode == "phi") {{
    PADDLE_ENFORCE_NE(
        this->phi_operants.get(),
        nullptr,
        common::errors::Unavailable(
            "The phi_operants pointer of OperantsManager is not initialized"));
    VLOG(4) << "OperantsManager reusing phi mode API paddle::experimental::{func_name}";
    return this->phi_operants->{func_name}({func_args_code});
  }} else {{
    PADDLE_THROW(common::errors::Unimplemented(
        "FLAGS_tensor_operants_mode is not nitialized, please set "
        "FLAGS_tensor_operants_mode first, which currently supports eager, "
        "phi, and static mode"));
  }}
"""

    def gene_operants_manager_implementation(self):
        func_name = self.get_api_func_name()
        final_code = ""
        # Codes for arthemetic operants
        if func_name in ["add", "subtract", "multiply", "divide"]:
            final_code += f"""
{self.get_return_type()} OperantsManager::{func_name}(const Tensor& x, const Scalar& y) {{{self.gene_operants_manager_code()}}}

{self.get_return_type()} OperantsManager::{func_name}(const Scalar& x, const Tensor& y) {{{self.gene_operants_manager_code()}}}
"""
        # Codes for specific operants
        if func_name in specific_ops_map.keys():
            final_code += f"""
{self.get_return_type()} OperantsManager::{specific_ops_map[func_name]}(const Tensor& x, const Tensor& y) {{{self.gene_operants_manager_code(is_specific_op=True)}}}

{self.get_return_type()} OperantsManager::{specific_ops_map[func_name]}(const Tensor& x, const Scalar& y) {{{self.gene_operants_manager_code(is_specific_op=True)}}}
"""
        # func decalaration
        if func_name[-1] != '_':
            return (
                final_code
                + f"""
{self.get_return_type()} OperantsManager::{func_name}({self.get_define_args()}) {{{self.gene_operants_manager_code()}}}
"""
            )
        else:
            return (
                final_code
                + f"""
{self.get_return_type(inplace_flag=True)} OperantsManager::{func_name}({self.get_define_args(inplace_flag=True)}) {{
{self.gene_operants_manager_code()}
}}
"""
            )


def generate_tensor_operants_api(
    api_yaml_path,
    operants_base_path,
    tensor_api_source_path,
    operants_header_path,
    operants_source_path,
    operants_manager_header_path,
    operants_manager_source_path,
    tensor_api_yaml_path,
):
    apis = []

    for each_api_yaml in api_yaml_path:
        with open(each_api_yaml, 'r') as f:
            api_list = yaml.load(f, Loader=yaml.FullLoader)
            if api_list:
                apis.extend(api_list)

    operants_base_file = open(operants_base_path, 'w')
    tensor_api_source_file = open(tensor_api_source_path, 'w')
    operants_header_file = open(operants_header_path, 'w')
    operants_source_file = open(operants_source_path, 'w')
    operants_manager_header_file = open(operants_manager_header_path, 'w')
    operants_manager_source_file = open(operants_manager_source_path, 'w')

    operants_base_file.write(operants_base_include)
    operants_base_file.write(operants_base_start)
    tensor_api_source_file.write(tensor_api_source_include)
    tensor_api_source_file.write(tensor_api_source_start)
    operants_header_file.write(operants_header_include)
    operants_header_file.write(operants_header_start)
    operants_source_file.write(operants_source_include)
    operants_source_file.write(operants_source_start)
    operants_manager_header_file.write(operants_manager_header_include)
    operants_manager_header_file.write(operants_manager_header_start)
    operants_manager_source_file.write(operants_manager_source_include)
    operants_manager_source_file.write(operants_manager_source_start)

    with open(tensor_api_yaml_path, 'rt') as f:
        api_prims = yaml.safe_load(f)

    for api in apis:
        operants_api = OperantsAPI(api, api_prims)
        if operants_api.is_prim_api:
            operants_base_file.write(operants_api.gene_operants_base())
            tensor_api_source_file.write(
                operants_api.gene_tensor_api_implementation()
            )
            operants_header_file.write(operants_api.gene_operants_declaration())
            operants_source_file.write(
                operants_api.gene_operants_implementation()
            )
            operants_manager_header_file.write(
                operants_api.gene_operants_declaration()
            )
            operants_manager_source_file.write(
                operants_api.gene_operants_manager_implementation()
            )

    operants_base_file.write(operants_base_end)
    tensor_api_source_file.write(tensor_api_source_end)
    operants_header_file.write(operants_header_end)
    operants_source_file.write(operants_source_end)
    operants_manager_header_file.write(operants_manager_header_end)
    operants_manager_source_file.write(operants_manager_source_end)

    operants_base_file.close()
    tensor_api_source_file.close()
    operants_header_file.close()
    operants_source_file.close()
    operants_manager_header_file.close()
    operants_manager_source_file.close()


def main():
    parser = argparse.ArgumentParser(
        description='Generate PaddlePaddle C++ API files'
    )
    parser.add_argument(
        '--api_yaml_path',
        help='path to api yaml file',
        nargs='+',
        default=['paddle/phi/ops/yaml/ops.yaml'],
    )

    parser.add_argument(
        '--operants_base_path',
        help='output of generated operants_base header code file',
        default='paddle/phi/api/include/operants_base.h',
    )

    parser.add_argument(
        '--tensor_api_source_path',
        help='output of generated tensor_api source code file',
        default='paddle/phi/api/lib/tensor_api.cc',
    )

    parser.add_argument(
        '--phi_tensor_operants_header_path',
        help='output of generated phi_tensor_operants header code file',
        default='paddle/phi/api/include/tensor_operants.h',
    )

    parser.add_argument(
        '--phi_tensor_operants_source_path',
        help='output of generated phi_tensor_operants source code file',
        default='paddle/phi/api/lib/tensor_operants.cc',
    )

    parser.add_argument(
        '--operants_manager_header_path',
        help='output of generated operants_manager header code file',
        default='paddle/phi/api/include/operants_manager.h',
    )

    parser.add_argument(
        '--operants_manager_source_path',
        help='output of generated operants_manager source code file',
        default='paddle/phi/api/lib/operants_manager.cc',
    )

    parser.add_argument(
        '--tensor_api_yaml_path',
        help='path to tensor_api yaml file',
        default='paddle/phi/api/lib/tensor_operants.yaml',
    )

    options = parser.parse_args()

    api_yaml_path = options.api_yaml_path
    operants_base_path = options.operants_base_path
    tensor_api_source_path = options.tensor_api_source_path
    operants_header_path = options.phi_tensor_operants_header_path
    operants_source_path = options.phi_tensor_operants_source_path
    operants_manager_header_path = options.operants_manager_header_path
    operants_manager_source_path = options.operants_manager_source_path
    tensor_api_yaml_path = options.tensor_api_yaml_path

    generate_tensor_operants_api(
        api_yaml_path,
        operants_base_path,
        tensor_api_source_path,
        operants_header_path,
        operants_source_path,
        operants_manager_header_path,
        operants_manager_source_path,
        tensor_api_yaml_path,
    )


if __name__ == '__main__':
    main()
