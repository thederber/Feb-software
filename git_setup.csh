git config branch.autosetuprebase always
git config status.submodulesummary 1
git config alias.sdiff "!git diff && git submodule foreach 'git diff'"
git config alias.spush "push --recurse-submodules=on-demand"
git config alias.strack "! git submodule foreach -q --recursive 'git checkout $(git config -f $toplevel/.gitmodules submodule.$name.branch || echo master)'"
git config alias.spull "!git pull --recurse-submodules && git submodule sync --recursive && git submodule update --init --remote --recursive --rebase && git strack"
git config push.recurseSubmodules on-demand
git config fetch.recurseSubmodules on-demand
git config pull.rebase preserve
git config diff.submodule log

git spull
