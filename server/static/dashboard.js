document.addEventListener("DOMContentLoaded", function () {
  const treeview = document.getElementById("treeview");
  const statusMessage = document.getElementById("status-message");
  const modal = document.getElementById("content-modal");
  const modalContent = document.getElementById("full-content");
  const closeModal = document.getElementsByClassName("close")[0];

  function toggleMenu(element) {
    const submenu = element.nextElementSibling;
    const arrow = element.querySelector(".arrow");
    if (submenu.style.display === "block") {
      submenu.style.display = "none";
      arrow.classList.remove("down");
    } else {
      submenu.style.display = "block";
      arrow.classList.add("down");
    }
  }

  function truncateContent(content, length = 30) {
    return content.length > length
      ? content.substring(0, length) + "..."
      : content;
  }

  function showModal(content) {
    modalContent.textContent = content;
    modal.style.display = "block";
  }

  closeModal.onclick = function () {
    modal.style.display = "none";
  };

  window.onclick = function (event) {
    if (event.target === modal) {
      modal.style.display = "none";
    }
  };

  function createTreeView(data) {
    treeview.innerHTML = "";
    data.forEach((pkg) => {
      const packageItem = document.createElement("div");
      packageItem.className = "treeview-item";
      const packageLabel = document.createElement("div");
      packageLabel.className = "treeview-item-label";
      packageLabel.innerHTML = `<span class="arrow">&#9654;</span> ${pkg.name}`;
      packageLabel.onclick = () => toggleMenu(packageLabel);
      packageItem.appendChild(packageLabel);

      const branchSubMenu = document.createElement("div");
      branchSubMenu.className = "treeview-submenu";
      branchSubMenu.style.display = "none"; // 默认隐藏
      pkg.branches.forEach((branch) => {
        const branchItem = document.createElement("div");
        branchItem.className = "treeview-item";
        const branchLabel = document.createElement("div");
        branchLabel.className = "treeview-item-label";
        branchLabel.innerHTML = `<span class="arrow">&#9654;</span> ${branch.name}`;
        branchLabel.onclick = () => toggleMenu(branchLabel);
        branchItem.appendChild(branchLabel);

        const details = document.createElement("div");
        details.className = "details";
        details.style.display = "none"; // 默认隐藏
        details.innerHTML = `
                      <table class="details-table">
                          <thead>
                              <tr>
                                  <th>包名</th>
                                  <th>分支名</th>
                                  <th>版本</th>
                                  <th>contentJson</th>
                                  <th>操作</th>
                              </tr>
                          </thead>
                          <tbody>
                              ${branch.packages
                                .map((packageDetail) => {
                                  const truncatedContent = truncateContent(
                                    packageDetail.contentJson,
                                    30
                                  );
                                  return `
                                      <tr>
                                          <td>${packageDetail.name}</td>
                                          <td>${branch.name}</td>
                                          <td>${packageDetail.version}</td>
                                          <td>${truncatedContent} <button class="view-content-button" data-content='${packageDetail.contentJson.replace(
                                    /'/g,
                                    "&apos;"
                                  )}'>查看</button></td>
                                          <td><button onclick="deletePackage('${
                                            packageDetail.name
                                          }','${branch.name}','${
                                    packageDetail.version
                                  }')">删除</button></td>
                                      </tr>
                                  `;
                                })
                                .join("")}
                          </tbody>
                      </table>
                  `;
        branchItem.appendChild(details);
        branchSubMenu.appendChild(branchItem);
      });
      packageItem.appendChild(branchSubMenu);
      treeview.appendChild(packageItem);
    });

    // 绑定查看按钮事件
    document.querySelectorAll(".view-content-button").forEach((button) => {
      button.addEventListener("click", function () {
        const content = this.getAttribute("data-content").replace(
          /&apos;/g,
          "'"
        );
        package_name = this.parentElement.parentElement.children[0].textContent;
        branch_name = this.parentElement.parentElement.children[1].textContent;
        version = this.parentElement.parentElement.children[2].textContent;
        console.log(`查看包 ${package_name} ${branch_name} ${version} 的内容`);
        url =
          "/getVersion?package=" +
          package_name +
          "&branch=" +
          branch_name +
          "&version=" +
          version;
        fetch(url)
          .then((response) => response.json())
          .then((data) => {
            res = data;
            if (res["status"] == 200) {
              showModal(
                JSON.stringify(JSON.parse(res["list"][0]["content"]), null, 4)
              );
            } else {
              showModal("无法获取内容");
            }
          })
          .catch((error) => {
            console.error("Error fetching content:", error);
            showModal("无法获取内容");
          });
      });
    });
  }

  async function fetchPackages() {
    try {
      const response = await fetch("/api/packages");
      if (!response.ok) throw new Error("Network response was not ok");
      const data = await response.json();
      statusMessage.style.display = "none";
      createTreeView(data);
    } catch (error) {
      console.error("Error fetching packages:", error);
      statusMessage.style.display = "block";
      statusMessage.textContent = "无法接通后端，显示演示数据。";
      const demoData = [
        {
          name: "test",
          branches: [
            {
              name: "major",
              packages: [
                {
                  id: "1",
                  name: "test",
                  version: "1.0.0",
                  contentJson: '{"key":"value"}',
                },
                {
                  id: "2",
                  name: "test",
                  version: "1.0.1",
                  contentJson: '{"key":"value1"}',
                },
              ],
            },
            {
              name: "minor",
              packages: [
                {
                  id: "5",
                  name: "test",
                  version: "1.0.2",
                  contentJson: '{"key":"value2"}',
                },
              ],
            },
          ],
        },
        {
          name: "hello",
          branches: [
            {
              name: "major",
              packages: [
                {
                  id: "2",
                  name: "hello",
                  version: "1.0.0",
                  contentJson: '{"key":"value"}',
                },
              ],
            },
          ],
        },
      ];
      createTreeView(demoData);
    }
  }

  // 每秒自动刷新
  // setInterval(fetchPackages, 1000);

  // 初始化加载数据
  fetchPackages();
});
function deletePackage(name, branch, version) {
  // 弹窗是否确认删除
  if (confirm(`确认删除包 ${name} ${branch} ${version} 吗？`)) {
    // 确认删除
    console.log(`删除包 ${name} ${branch} ${version}`);
    url =
      "/api/deletePackage?package=" +
      name +
      "&branch=" +
      branch +
      "&version=" +
      version;
    fetch(url)
      .then((response) => response.json())
      .then((data) => {
        res = data;
        if (res["status"] == 200) {
          alert("删除成功");
          window.location.reload();
        } else {
          alert("删除失败");
        }
      })
      .catch((error) => {
        console.error("Error deleting package:", error);
        alert("删除失败");
      });
  }
  // 请求后端删除包的API
}
