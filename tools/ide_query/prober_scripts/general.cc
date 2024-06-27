#include <vector>

#include "testdata.pb.h"

using ide_query::prober_scripts::ProtoMsg;

void TestCompletion() {
  // Test completion on protos and fuzzy matching of completion suggestions.

  ProtoMsg foo;

  // ^

  // step
  // repo.waitForReady()
  // type("f")
  // completion.trigger()
  // assert completion.items.filter(label="foo")
  // delline()
  // type("foo.sf")
  // completion.trigger()
  // assert completion.items.filter(
  //  label="some_field.*",
  //  insertText="some_field.*",
  // )
  // delline()

  // ^

  // step
  // repo.waitForReady()
  // type("slf")
  // completion.trigger()
  // assert completion.items.filter(
  //  label="absl::SleepFor.*",
  //  insertText="absl::SleepFor.*",
  //  documentation="(?s).*Sleeps for the specified duration.*",
  // )
  // delline()
  // type("sec")
  // completion.trigger()
  // assert completion.items.filter(
  //  label="absl::Seconds.*",
  //  insertText="absl::Seconds.*",
  // )
  // delline()
  // type("strj")
  // completion.trigger()
  // assert completion.items.filter(label="absl::StrJoin.*")
  // delline()

  std::vector<int> v;

  // ^

  // step
  // repo.waitForReady()
  // type("v.push")
  // completion.trigger()
  // assert completion.items.filter(label="push_back.*")
  // delline()
}

int main() { return 0; }
