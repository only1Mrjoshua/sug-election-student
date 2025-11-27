// Auto-detect environment and set API base URL
      function getApiBaseUrl() {
        const hostname = window.location.hostname;
        const port = window.location.port;

        if (hostname === "localhost" || hostname === "127.0.0.1") {
          document.getElementById("environment-badge").textContent =
            "LOCALHOST";
          document.getElementById("environment-badge").style.background =
            "#d13d39";
          return `http://localhost:5001/api`;
        } else {
          document.getElementById("environment-badge").textContent = "LIVE";
          document.getElementById("environment-badge").style.background =
            "#2c8a45";
          // Replace with your actual Render URL
          return `https://obong-university-src-election-portal-muyc.onrender.com/api`;
        }
      }

      const API_BASE = getApiBaseUrl();
      let selectedCandidates = {};
      let isStudentVerified = false;
      let allCandidates = [];
      let allPositions = [];
      let currentVoterId = "";
      let currentVoterName = "";
      let currentElectionStatus = "not_started";

      // Load election status on page load
      async function loadElectionStatus() {
        try {
          console.log(
            `🌐 Fetching election status from: ${API_BASE}/election-status`
          );
          const response = await fetch(API_BASE + "/election-status");

          if (!response.ok) {
            throw new Error(`HTTP error! status: ${response.status}`);
          }

          const result = await response.json();

          if (result.success) {
            currentElectionStatus = result.election_status;
            updateElectionStatusBanner();
          } else {
            throw new Error(result.message || "Failed to load election status");
          }
        } catch (error) {
          console.error("Failed to load election status:", error);
          const banner = document.getElementById("election-status-banner");
          const statusText = document.getElementById("election-status-text");
          banner.className = "election-status ended";
          statusText.innerHTML = `<strong>Connection Error:</strong> Unable to connect to election server. Please check your connection.`;
        }
      }

      // Update election status banner
      function updateElectionStatusBanner() {
        const banner = document.getElementById("election-status-banner");
        const statusText = document.getElementById("election-status-text");

        banner.className = "election-status " + currentElectionStatus;

        switch (currentElectionStatus) {
          case "ongoing":
            statusText.innerHTML =
              "<strong>Voting is currently ongoing.</strong> You can verify your Voter ID and cast your vote.";
            break;
          case "paused":
            statusText.innerHTML =
              "<strong>Voting has been temporarily paused.</strong> Please check back later.";
            break;
          case "ended":
            statusText.innerHTML =
              "<strong>Voting has ended.</strong> Thank you for participating.";
            break;
          default:
            statusText.innerHTML =
              "<strong>Voting has not started yet.</strong> Please wait for the election to begin.";
        }
      }

      // Tab navigation
      document.querySelectorAll(".tab").forEach((item) => {
        item.addEventListener("click", function () {
          if (this.getAttribute("data-tab") === "vote" && !isStudentVerified) {
            const alert = document.getElementById("verify-alert");
            alert.className = "alert alert-error";
            alert.innerHTML = `<i class="fas fa-exclamation-circle"></i> You must verify your Voter ID first before accessing the voting page.`;
            alert.style.display = "flex";
            showTab("verify");
            return;
          }

          document.querySelectorAll(".tab").forEach((tab) => {
            tab.classList.remove("active");
          });

          this.classList.add("active");

          document.querySelectorAll(".tab-content").forEach((tab) => {
            tab.classList.remove("active");
          });

          const tabId = this.getAttribute("data-tab") + "-tab";
          document.getElementById(tabId).classList.add("active");

          if (this.getAttribute("data-tab") === "vote" && isStudentVerified) {
            loadCandidates();
          }
        });
      });

      function showTab(tabName) {
        if (tabName === "vote" && !isStudentVerified) {
          const alert = document.getElementById("verify-alert");
          alert.className = "alert alert-error";
          alert.innerHTML = `<i class="fas fa-exclamation-circle"></i> You must verify your Voter ID first before accessing the voting page.`;
          alert.style.display = "flex";
          return;
        }

        document.querySelectorAll(".tab").forEach((tab) => {
          tab.classList.remove("active");
          if (tab.getAttribute("data-tab") === tabName) {
            tab.classList.add("active");
          }
        });

        document.querySelectorAll(".tab-content").forEach((tab) => {
          tab.classList.remove("active");
        });

        document.getElementById(`${tabName}-tab`).classList.add("active");

        if (tabName === "vote" && isStudentVerified) {
          loadCandidates();
        }
      }

      function enableVotingTab(voterId, voterName) {
        const voteTab = document.getElementById("vote-tab-button");
        voteTab.classList.remove("disabled");
        isStudentVerified = true;
        currentVoterId = voterId;
        currentVoterName = voterName;

        // Update voter info display
        document.getElementById("display-voter-id").textContent = voterId;
        document.getElementById("display-voter-name").textContent = voterName;
        document.getElementById("voter-info").style.display = "block";

        document.getElementById("access-denied-view").style.display = "none";
        document.getElementById("voting-view").style.display = "block";
      }

      // Voter ID verification form handler
      document
        .getElementById("voter-verification-form")
        .addEventListener("submit", async (e) => {
          e.preventDefault();

          if (currentElectionStatus !== "ongoing") {
            const alert = document.getElementById("verify-alert");
            alert.className = "alert alert-error";
            let message = "";

            switch (currentElectionStatus) {
              case "not_started":
                message =
                  "Voting has not started yet. Please wait for the election to begin.";
                break;
              case "paused":
                message =
                  "Voting has been temporarily paused. Please try again later.";
                break;
              case "ended":
                message = "Voting has ended. You can no longer cast your vote.";
                break;
              default:
                message =
                  "Voting is currently unavailable. Please try again later.";
            }

            alert.innerHTML = `<i class="fas fa-exclamation-circle"></i> ${message}`;
            alert.style.display = "flex";
            return;
          }

          const voterId = document.getElementById("voter-id").value.trim();
          const verifyBtn = document.getElementById("verify-btn");

          if (!voterId) {
            const alert = document.getElementById("verify-alert");
            alert.className = "alert alert-error";
            alert.innerHTML = `<i class="fas fa-exclamation-circle"></i> Voter ID is required.`;
            alert.style.display = "flex";
            return;
          }

          try {
            verifyBtn.innerHTML =
              '<i class="fas fa-spinner fa-spin"></i> Verifying...';
            verifyBtn.disabled = true;

            console.log(`🌐 Verifying Voter ID at: ${API_BASE}/verify-voter`);
            const response = await fetch(API_BASE + "/verify-voter", {
              method: "POST",
              headers: { "Content-Type": "application/json" },
              body: JSON.stringify({ voter_id: voterId }),
            });

            if (!response.ok) {
              throw new Error(`HTTP error! status: ${response.status}`);
            }

            const result = await response.json();
            const alert = document.getElementById("verify-alert");

            if (result.success) {
              if (result.verified && result.can_vote) {
                alert.className = "alert alert-success";
                alert.innerHTML = `<i class="fas fa-check-circle"></i> ${result.message}`;
                alert.style.display = "flex";
                enableVotingTab(result.voter_id, result.voter_name);
                setTimeout(() => {
                  showTab("vote");
                }, 1500);
              } else if (result.verified && !result.can_vote) {
                alert.className = "alert alert-error";
                alert.innerHTML = `<i class="fas fa-exclamation-circle"></i> ${result.message}`;
                alert.style.display = "flex";
              } else {
                alert.className = "alert alert-error";
                alert.innerHTML = `<i class="fas fa-exclamation-circle"></i> ${result.message}`;
                alert.style.display = "flex";
              }
            } else {
              alert.className = "alert alert-error";
              alert.innerHTML = `<i class="fas fa-exclamation-circle"></i> ${result.message}`;
              alert.style.display = "flex";
            }
          } catch (error) {
            const alert = document.getElementById("verify-alert");
            alert.className = "alert alert-error";
            alert.innerHTML =
              '<i class="fas fa-exclamation-circle"></i> Verification failed. Please check your connection and try again.';
            alert.style.display = "flex";
          } finally {
            verifyBtn.innerHTML =
              '<i class="fas fa-search"></i> Verify Voter ID';
            verifyBtn.disabled = false;
          }
        });

      // Update vote button state
      function updateVoteButtonState() {
        const voteBtn = document.getElementById("vote-btn");
        const allPositionsSelected = allPositions.every(
          (position) => selectedCandidates[position]
        );

        if (allPositionsSelected) {
          voteBtn.disabled = false;
          voteBtn.innerHTML =
            '<i class="fas fa-paper-plane"></i> Submit Your Vote';
        } else {
          voteBtn.disabled = true;
          voteBtn.innerHTML =
            '<i class="fas fa-exclamation-circle"></i> Select All Positions First';
        }
      }

      // Load candidates for voting
      async function loadCandidates() {
        const container = document.getElementById("candidates-container");

        try {
          container.innerHTML = `
                    <div class="loading">
                        <div class="loading-spinner"></div>
                        <p>Loading candidates...</p>
                    </div>
                `;

          console.log(`🌐 Fetching candidates from: ${API_BASE}/candidates`);
          const response = await fetch(API_BASE + "/candidates");

          if (!response.ok) {
            throw new Error(`HTTP error! status: ${response.status}`);
          }

          const result = await response.json();

          if (result.success) {
            allCandidates = result.candidates;
            container.innerHTML = "";

            if (allCandidates && allCandidates.length > 0) {
              const positions = {};
              allPositions = [];

              allCandidates.forEach((candidate) => {
                if (!positions[candidate.position]) {
                  positions[candidate.position] = [];
                  allPositions.push(candidate.position);
                }
                positions[candidate.position].push(candidate);
              });

              for (const [position, candidates] of Object.entries(positions)) {
                const positionSection = document.createElement("div");
                positionSection.className = "position-section";

                const positionHeader = document.createElement("div");
                positionHeader.className = "position-title";

                const isSelected = !!selectedCandidates[position];

                positionHeader.innerHTML = `
                                <span>${position}</span>
                                <span class="position-status ${
                                  isSelected
                                    ? "status-completed"
                                    : "status-required"
                                }">
                                    ${isSelected ? "Selected" : "Required"}
                                </span>
                            `;
                positionSection.appendChild(positionHeader);

                const candidatesGrid = document.createElement("div");
                candidatesGrid.className = "candidates-grid";

                candidates.forEach((candidate) => {
                  const candidateCard = document.createElement("div");
                  candidateCard.className = "candidate-card";
                  if (
                    selectedCandidates[position] &&
                    selectedCandidates[position].id === candidate.id
                  ) {
                    candidateCard.classList.add("selected");
                  }
                  candidateCard.dataset.candidateId = candidate.id;
                  candidateCard.dataset.position = candidate.position;
                  candidateCard.innerHTML = `
                                    <div class="candidate-name">${
                                      candidate.name
                                    }</div>
                                    ${
                                      candidate.faculty
                                        ? `<div class="candidate-faculty">${candidate.faculty}</div>`
                                        : ""
                                    }
                                `;

                  candidateCard.addEventListener("click", function () {
                    const position = this.dataset.position;
                    const candidateId = this.dataset.candidateId;
                    const candidateName =
                      this.querySelector(".candidate-name").textContent;

                    document
                      .querySelectorAll(
                        `.candidate-card[data-position="${position}"]`
                      )
                      .forEach((card) => {
                        card.classList.remove("selected");
                      });

                    this.classList.add("selected");
                    selectedCandidates[position] = {
                      id: candidateId,
                      name: candidateName,
                    };

                    const positionHeader =
                      this.closest(".position-section").querySelector(
                        ".position-title"
                      );
                    positionHeader.querySelector(".position-status").className =
                      "position-status status-completed";
                    positionHeader.querySelector(
                      ".position-status"
                    ).textContent = "Selected";

                    updateVoteButtonState();
                  });

                  candidatesGrid.appendChild(candidateCard);
                });

                positionSection.appendChild(candidatesGrid);
                container.appendChild(positionSection);
              }

              updateVoteButtonState();
            } else {
              container.innerHTML = `
                            <div class="loading">
                                <i class="fas fa-users" style="font-size: 3rem; margin-bottom: 20px; opacity: 0.5;"></i>
                                <h3>No Candidates Available</h3>
                                <p>Candidates will appear here once they are registered.</p>
                            </div>
                        `;
            }
          } else {
            throw new Error(result.message || "Failed to load candidates");
          }
        } catch (error) {
          container.innerHTML = `
                    <div class="loading">
                        <i class="fas fa-exclamation-triangle" style="font-size: 3rem; margin-bottom: 20px; color: var(--primary-red);"></i>
                        <h3>Unable to Load Candidates</h3>
                        <p>There was a problem fetching the candidate list. Please try again.</p>
                        <button class="btn" style="margin-top: 20px;" onclick="loadCandidates()">
                            <i class="fas fa-redo"></i>
                            Try Again
                        </button>
                    </div>
                `;
        }
      }

      // Voting form handler
      document
        .getElementById("voting-form")
        .addEventListener("submit", async (e) => {
          e.preventDefault();

          if (currentElectionStatus !== "ongoing") {
            const alert = document.getElementById("vote-alert");
            alert.className = "alert alert-error";
            let message = "";

            switch (currentElectionStatus) {
              case "not_started":
                message =
                  "Voting has not started yet. Please wait for the election to begin.";
                break;
              case "paused":
                message =
                  "Voting has been temporarily paused. Please try again later.";
                break;
              case "ended":
                message = "Voting has ended. You can no longer cast your vote.";
                break;
              default:
                message =
                  "Voting is currently unavailable. Please try again later.";
            }

            alert.innerHTML = `<i class="fas fa-exclamation-circle"></i> ${message}`;
            alert.style.display = "flex";
            return;
          }

          const missingPositions = allPositions.filter(
            (position) => !selectedCandidates[position]
          );
          if (missingPositions.length > 0) {
            const alert = document.getElementById("vote-alert");
            alert.className = "alert alert-error";
            alert.innerHTML = `<i class="fas fa-exclamation-circle"></i> Please select one candidate for every position before submitting your vote.`;
            alert.style.display = "flex";
            return;
          }

          const voteBtn = document.getElementById("vote-btn");
          const originalText = voteBtn.innerHTML;

          try {
            voteBtn.innerHTML =
              '<i class="fas fa-spinner fa-spin"></i> Submitting Votes...';
            voteBtn.disabled = true;

            console.log(`🌐 Submitting votes to: ${API_BASE}/vote`);
            const response = await fetch(API_BASE + "/vote", {
              method: "POST",
              headers: { "Content-Type": "application/json" },
              body: JSON.stringify({
                voter_id: currentVoterId,
                voter_name: currentVoterName,
                votes: selectedCandidates,
              }),
            });

            if (!response.ok) {
              throw new Error(`HTTP error! status: ${response.status}`);
            }

            const result = await response.json();
            const alert = document.getElementById("vote-alert");

            if (result.success) {
              document.getElementById("voting-section").style.display = "none";
              document.getElementById("vote-confirmation").style.display =
                "block";
            } else {
              alert.className = "alert alert-error";
              alert.innerHTML = `<i class="fas fa-exclamation-circle"></i> ${result.message}`;
              alert.style.display = "flex";
              voteBtn.innerHTML = originalText;
              voteBtn.disabled = false;
            }
          } catch (error) {
            const alert = document.getElementById("vote-alert");
            alert.className = "alert alert-error";
            alert.innerHTML =
              '<i class="fas fa-exclamation-circle"></i> Voting failed. Please check your connection and try again.';
            alert.style.display = "flex";
            voteBtn.innerHTML = originalText;
            voteBtn.disabled = false;
          }
        });

      // Initialize the page
      document.addEventListener("DOMContentLoaded", () => {
        console.log(`🚀 Election Portal Initialized`);
        console.log(`🌐 API Base URL: ${API_BASE}`);
        console.log(`🏠 Current Host: ${window.location.hostname}`);

        loadElectionStatus();
        document
          .querySelector('.tab[data-tab="verify"]')
          .addEventListener("click", () => {
            document.getElementById("voter-verification-form").reset();
            document.getElementById("verify-alert").style.display = "none";
          });
      });